import os
import ffmpeg
import uuid
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'flac'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            return redirect(url_for('transcribe',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def transcribe(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

# Use ffmpeg to convert our file to WAV @ 16k
def normalize_file(file):
    filename = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + ".wav")
    stream = ffmpeg.input(file)
    stream = ffmpeg.output(stream, filename, format='s16le', acodec='pcm_s16le', ac=1, ar='16k')
    # stream = ffmpeg.overwrite_output(stream)
    ffmpeg.run(stream)
    return filename
