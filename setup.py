#!/usr/bin/env python
from distutils.core import setup

setup(name='deepspeech-frontend',
      version="0.9.3",
      description='Recieves API calls and returns text.',
      author='Dan Ryan',
      author_email='dan@acceleratenetworks.com',
      url='https://git.callpipe.com/fusionpbx/deepspeech_frontend',
      packages=['deepspeech_frontend'],
      install_requires=['ffmpeg-python', 'flask', 'deepspeech', 'uuid', 'requests', 'scipy'])
