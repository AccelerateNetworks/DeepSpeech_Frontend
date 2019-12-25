import os
import ffmpeg
import uuid
import time
from deepspeech import Model
import scipy.io.wavfile as wav
from flask import Flask, flash, request, redirect, url_for, send_from_directory, make_response, jsonify
from werkzeug.utils import secure_filename

# These constants control the beam search decoder

# Beam width used in the CTC decoder when building candidate transcriptions
BEAM_WIDTH = 500

# Alpha hyperparameter of the CTC decoder. Language Model weight (aka LM_Alpha)
LM_WEIGHT = 0.75

# Valid word insertion weight. This is used to lessen the word insertion penalty
# when the inserted word is part of the vocabulary (aka LM_Beta)
VALID_WORD_COUNT_WEIGHT = 1.85

# These constants are tied to the shape of the graph used (changing them changes
# the geometry of the first layer), so make sure you use the same constants that
# were used during training




UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'flac'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ds = Model('models/output_graph.pb', BEAM_WIDTH)
ds.enableDecoderWithLM('models/lm.binary', 'models/trie', LM_WEIGHT,
                       VALID_WORD_COUNT_WEIGHT)
api_keys = []
api_keyfile = 'api_keys.txt'
transcription_in_progress = False
print(transcription_in_progress)


def load_keys(keylist):
    with open(keylist) as f:
        for line in f:
            credential = line.split(', ')
            api_keys.append(credential[0])

if os.path.isfile(api_keyfile):
    load_keys(api_keyfile)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            fileLocation = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(fileLocation)
            convertedFile = normalize_file(fileLocation)
            os.remove(fileLocation)
            return redirect(url_for('transcribe',
                                    filename=convertedFile))
    return '''
    <!doctype html>
    <center><title>Upload an Audio File</title>
    <h1>Upload your audio file</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    <br>
    <p>We accept wav, mp3 and flac, after uploading you'll be redirected to a transcribed version of your file.</p>
    <p>No files or text is retained after a file is processed, we use Mozilla's DeepSpeech library with their default models and settings,
    To contribute, come <a href="https://git.callpipe.com/fusionpbx/deepspeech_frontend/">check out our code</a>! We're also looking for suggestions as how to improve accuracy.</p></center>
    '''

@app.route('/results/<filename>')
def transcribe(filename):
    global transcription_in_progress
    if(transcription_in_progress):
        print("Oh no! Another transcription was in progress, waiting 5 seconds...")
        time.sleep(5)
        transcribe(filename)
    print("Starting transcription...")
    transcription_in_progress = True
    fs, audio = wav.read(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    processed_data = ds.stt(audio)
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    transcription_in_progress = False
    return processed_data

# Use ffmpeg to convert our file to WAV @ 16k
def normalize_file(file):
    filename = str(uuid.uuid4()) + ".wav"
    fileLocation = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    stream = ffmpeg.input(file)
    stream = ffmpeg.output(stream, fileLocation, acodec='pcm_s16le', ac=1, ar='16k')
    ffmpeg.run(stream)
    return filename

@app.route('/api/v1/process', methods=['POST'])
def api_transcribe():
    # check and see if API keys are set
    if(len(api_keys) > 0):
        # get the request headers and check the keys
        if "Authorization" in request.headers:
            key = request.headers["Authorization"]
            if(len(key) > 7):
                if key[7:] not in api_keys:
                    return make_response(jsonify({'error': 'Your API key is invalid :c'}), 400)
            else:
                return make_response(jsonify({'error': 'Your API key was empty :c'}), 400)
        else:
            return make_response(jsonify({'error': 'We need an API key to process your request :c'}), 400)

    # check if the post request has the file part
    if 'file' not in request.files:
        return make_response(jsonify({'error': 'No file part'}), 400)
    file = request.files['file']
    # if the request has a blank filename
    if file.filename == '':
        return make_response(jsonify({'error': 'No file in file parameter'}), 400)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        fileLocation = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(fileLocation)
        convertedFile = normalize_file(fileLocation)
        # stream = ffmpeg.overwrite_output(stream)
        os.remove(fileLocation)

        return jsonify({'message' : transcribe(filename=convertedFile)})
    return make_response(jsonify({'error': 'Something went wrong :c'}), 400)

# Return a JSON error rather than a HTTP 404
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
