#!/usr/bin/env python
import deepspeech_frontend
import os.path
import requests
# import tarfile

if os.path.isfile("models/output_graph.pb") or os.path.isfile("models/alphabet.txt"):
    print("Starting the DeepSpeech Frontend")
    deepspeech_frontend.app.run(debug=True, host="::")
else:
    # print("Looks like your missing the DeepSpeech Voice Model, downloading them now (1.4GB).")
    # # urllib.request.urlretrieve("https://github.com/mozilla/DeepSpeech/releases/download/v0.1.1/deepspeech-0.1.1-models.tar.gz", "deepspeech-0.1.1-models.tar.gz")
    # response = requests.get("https://github.com/mozilla/DeepSpeech/releases/download/v0.1.1/deepspeech-0.1.1-models.tar.gz", stream=True)
    # handle = open("deepspeech-0.1.1-models.tar.gz", "wb")
    # count = 0
    # for chunk in response.iter_content(chunk_size=512):
    #     count += 1
    #     # Lets not spam the terminal too much! Showing progress every 100MB
    #     if count % 100000:
    #         print(str(count/100000) + "MB Downloaded")
    #     if chunk:  # filter out keep-alive new chunks
    #         handle.write(chunk)
    #
    # print("Download completed, unzipping the DeepSpeech Voice Model")
    # tar = tarfile.open("deepspeech-0.1.1-models.tar.gz")
    # tar.extractall()
    # tar.close()
    # print("Starting the DeepSpeech Frontend")
    # deepspeech_frontend.app.run(debug=True, host="::")
    print("Please go download the DeepSpeech Voice Model and unzip it. It should unzip to a directory called models inside this directory!")
