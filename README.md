# aud v0.1.18

aud is an audio package meant to help streamline batch audio edits.
It allows you to easily work with complex file structures and naming conventions.
It is also meant to be easy enough for a beginner programmer to dive in and use.
The foundation of this package relies on two core pieces; FFMPEG and PyDub.

AudDir allows you perform batch audio actions on messy folders.
When working with audio you may often end up with many arbitrary files your DAW may produce so AudDir allows you to point only to specific extensions in a directory and to work with them on the fly.

## Getting Started

Getting started with aud is simple!
Simply import and start playing with your files.

```
from aud import AudDir

# which files to operate on
ad = AudDir('samples/')

# which extensions in the folder to operate on
ad.extensions = ['.wav', '.mp3']

# which folder to output to when changing audio files
ad.setOutputDir("_Processed")

# rename all of the selected files
ad.renameUpper()
ad.renamePrepend('FX_')

# finally create new files of the desired type in our output location
ad.convertTo(_extension=".wav", _target_samplerate=44100, _target_bitdepth=16)
```

### Prerequisites

What things you need to install the software and how to install them

```
>> python3
>> pip3
>> ffmpeg
>> ffmpeg-normalize
```

### Installing

Install prerequisites

```
ON LINUX:
>> sudo apt install python3
>> sudo python3 -m pip install pip
>> sudo add-apt-repository ppa:mc3man/trusty-media
>> sudo apt update
>> sudo apt install ffmpeg
>> sudo python3 -m pip install ffmpeg-normalize
```

And install aud

```
>> sudo python3 -m pip install aud
```

Refer to example.py to see more in depth examples
