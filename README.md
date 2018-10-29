# DeepSpeech Frontend

A simple flask app that transcribes files served to it via HTTP POST, and redirects the user to the text we were able to get from their audio.

## Installation
Install the dependencies, for Debian that would look like this:

```
apt install python3-pip git ffmpeg
```
Creating a virtual environment is recommended:

```
virtualenv -p python3 env
. env/bin/activate
```

Followed by installing the python packages needed:

```
pip install ffmpeg-python flask deepspeech
pip install git+https://git.callpipe.com/fusionpbx/deepspeech_frontend
```

At this point, Mozilla's DeepSpeech needs a language model:
```
wget -O - https://github.com/mozilla/DeepSpeech/releases/download/v0.3.0/deepspeech-0.3.0-models.tar.gz | tar xvfz -
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

## Optimizations
Based on our testing, a box with 1GB of Ram is the bare minimum needed to run DeepSpeech, though more is recommended. If you have spare hardware resources, edit the configuration in `deepspeech_frontend/__init__.py` on line 36, changing `models/output_graph.pbmm` to `models/output_graph.pb` to reference the normal voice model rather than the mmap-able model. This should reduce how much your system swaps or hits disk (as the model will be loaded into ram), but note that it seems to eat ram for breakfast!

When using an mmap-able model, we saw memory usage reduced significantly, and according to [lissyx in this thread](https://discourse.mozilla.org/t/error-while-running-sample-model-on-raspbian-gnu-linux-9-4-stretch/28599/4) it should make DeepSpeech able to run on Single Board Computers like the OrangePi PC or Raspberry Pi.

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
* Ram usage seems to increase drastically on longer files, slice audio files into smaller parts.
* Queue for recordings to be processed
* Add endpoints that act like standard proprietary HTTP voice endpoints (making this a drop in replacement)
* Add GPU support
* Try using a [punctuation adding script](https://github.com/alpoktem/punkProse)
* Perhaps pass the output through a spellchecker, and fix simple cases like capitalizing I and the first letter of the string generated.
