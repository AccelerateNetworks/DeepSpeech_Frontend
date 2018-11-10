#!/usr/bin/env python
import deepspeech_frontend
import os.path
import requests

if os.path.isfile("models/output_graph.pb") or os.path.isfile("models/alphabet.txt"):
    print("Starting the DeepSpeech Frontend")
    deepspeech_frontend.app.run(debug=True, host="::")
else:
    print("Please go download the DeepSpeech Voice Model and unzip it. It should unzip to a directory called models inside this directory!")
