import os
import ffmpeg
import uuid
import webrtcvad
from .chunker import read_wave, write_wave, frame_generator, vad_collector
from deepspeech import Model
import scipy.io.wavfile as wav
from flask import Flask, flash, request, redirect, url_for, send_from_directory, make_response, jsonify
from werkzeug.utils import secure_filename

# These constants control the beam search decoder

# Beam width used in the CTC decoder when building candidate transcriptions
BEAM_WIDTH = 500

# The alpha hyperparameter of the CTC decoder. Language Model weight
LM_WEIGHT = 1.50

# Valid word insertion weight. This is used to lessen the word insertion penalty
# when the inserted word is part of the vocabulary
VALID_WORD_COUNT_WEIGHT = 2.10

# These constants are tied to the shape of the graph used (changing them changes
# the geometry of the first layer), so make sure you use the same constants that
# were used during training

# Number of MFCC features to use
N_FEATURES = 26

# Size of the context window used for producing timesteps in the input vector
N_CONTEXT = 9

# How aggressive to be when splitting audio files into chunks
aggressiveness = 1

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'flac'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ds = Model('models/output_graph.pbmm', N_FEATURES, N_CONTEXT, 'models/alphabet.txt', BEAM_WIDTH)
ds.enableDecoderWithLM('models/alphabet.txt', 'models/lm.binary', 'models/trie', LM_WEIGHT,
                       VALID_WORD_COUNT_WEIGHT)
api_keys = []
api_keyfile = 'api_keys.txt'
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
    processed_data = ""
    audio, sample_rate = read_wave(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    vad = webrtcvad.Vad(0)
    frames = frame_generator(20, audio, sample_rate)
    frames = list(frames)
    # Change the frame generator line above and the frame size (20 by default)/window size (40 by default) when dealing with non-stop talkers!
    segments = vad_collector(sample_rate, 20, 40, vad, frames)
    for i, segment in enumerate(segments):
        path = 'chunk-%002d.wav' % (i,)
        # print(' Writing %s' % (path,))
        write_wave(path, segment, sample_rate)
        fs, audio = wav.read(path)
        processed_data += ds.stt(audio, fs)
        processed_data += " "
        # print(processed_data)
        os.remove(path)
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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
    print(request.headers)
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

def load_keys(keylist):
    with open(keylist) as f:
        for line in f:
            credential = line.split(', ')
            api_keys.append(credential[0])
