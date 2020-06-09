# DeepSpeech Frontend

A flask app that transcribes files served to it via HTTP POST, and redirects the user to the text we were able to get from their audio.

## Installation
Install the dependencies, for Debian that would look like this:

```
apt update && apt install python3-pip git ffmpeg python3-virtualenv wget
git clone https://git.callpipe.com/fusionpbx/deepspeech_frontend
cd deepspeech_frontend
```
Creating a virtual environment is recommended:

```
python3 /usr/lib/python3/dist-packages/virtualenv.py -p python3 env
. env/bin/activate
```

Followed by installing the python packages needed:

```
pip install -r requirements.txt
```

At this point, Mozilla's DeepSpeech needs a language model:
```
mkdir models && cd models && wget https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.pbmm && wget https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.scorer
```

Now, lets take this for a test spin!
```
python run.py
```
Navigate to http://localhost:5000/ in a web browser and upload your audio file. Once transcribed, you'll be redirected to the transcription.

## Production Use
Next, you'll probably want to install something to serve it with, rather than the flask built in web server.
`gunicorn` is what I use:

```
apt update && apt install gunicorn3 python3-pip git ffmpeg wget 
mkdir /var/lib/deepspeech/ && /var/lib/deepspeech/models && cd /var/lib/deepspeech/models
wget https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.pbmm && wget https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.scorer
pip3 install git+https://git.callpipe.com/fusionpbx/deepspeech_frontend.git
pip3 install -r requirements.txt
```

Finally, run gunicorn to start the server:

```
gunicorn -b 0.0.0.0 deepspeech_frontend:app
```

You may want this running as a daemon and probably managed by your init system, take a look at
`deepspeech_frontend.service` in this directory for a sample systemd unit file, you will likely need to modify it
to your liking.

## Configuration
Configuration is done in the beginning of `deepspeech_frontend/__init__.py`. You can modify the directory where uploaded and not yet fully processed files are temporarily stored, change the language model and more.

Adding an api_keys.txt to the base directory will restrict the API to authenticated users with valid API keys. The file format is simple with `<API_Key>, anything you want` on each line. To use a key, the API expects to be accessed with something equivalent to `curl -X POST <server>/api/v1/process -H 'Authorization: Bearer <api_key>' -F file=@<your_audio_file>`.

## References Used
Thanks to the following people and resources, this project exists:
* thefinn93 - https://github.com/thefinn93/webhook-receiver
   * Helped me with Python Q&A
   * Let me use his README & systemd unit file as a template
* Ashraff Hathibelagal - https://progur.com/2018/02/how-to-use-mozilla-deepspeech-tutorial.html
   * Provided great examples on how to work with Mozilla's DeepSpeech
* Mozilla's DeepSpeech - https://github.com/mozilla/DeepSpeech
* Flask's Documentation Writers - http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
* FFmpeg-Python - https://github.com/kkroening/ffmpeg-python/

## Things to improve
* Queue for recordings to be processed
* Add endpoints that act like standard proprietary HTTP voice endpoints (making this a drop in replacement)
* Add GPU support
