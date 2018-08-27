# DeepSpeech Frontend

A simple flask app that transcribes files served to it via HTTP POST, and redirects the user to the text we were able to get from their audio.

## Installation
Creating a virtual environment is recommended:

```
virtualenv -p python3 env
. env/bin/activate
```

Followed by installing the dependecies:

```
pip install ffmpeg-python flask deepspeech
```

To install the latest version of this app, you can use pip:

```
pip install git+https://git.callpipe.com/fusionpbx/deepspeech_frontend
```

At this point, Mozilla's DeepSpeech needs a language model:
```
wget https://github.com/mozilla/DeepSpeech/releases/download/v0.1.1/deepspeech-0.1.1-models.tar.gz
tar -xvzf deepspeech-0.1.1-models.tar.gz
```

Next, you'll probably want to install something to serve it with, rather than the flask built in web server.
`gunicorn` is what I use:

```
pip install gunicorn
```

Finally, run gunicorn to start the server:

```
gunicorn -b 0.0.0.0 deepspeech_frontend:app
```

You may want this running as a daemon and probably managed by your init system, take a look at
`deepspeech_frontend.service` in this directory for a sample systemd unit file, you will likely need to modify it
to your liking.

## Configuration
Configuration is done in the beginning of `deepspeech_frontend/__init__.py`. You can modify the directory where uploaded and transcoded files are temporarily stored, change the language model and weights used and more.

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
* Add GPU support
* Find or make a voice model that works better for handling short voicemails (the current voice model seems to be using phonics)
* Perhaps pass the output through a spellchecker, and fix simple cases like capitalizing I and the first letter of the string generated.
