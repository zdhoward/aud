# aud
### v0.8.5
[![CircleCI](https://circleci.com/gh/zdhoward/aud.svg?style=svg)](https://circleci.com/gh/zdhoward/aud)

- Support for Python 3.8, 3.7, & 3.6
- Support for Windows & Ubuntu
- Requires ffmpeg is already installed and updated

##### Installing FFMPEG:
```
>> On Linux:
apt-get install ffmpeg libavcodec-extra

>> On Mac:
brew install ffmpeg --with-libvorbis --with-sdl2 --with-theora

>> On Windows:
>> visit https://www.ffmpeg.org/download.html
>> download and install the appropriate package
>> ensure it is added to your PATH and you can call it from cmd
```

##### To start contributing:
```
>> git clone https://github.com/zdhoward/aud.git
>> cd aud
>> virtualenv venv
>> source venv/bin/activate
>> python3 -m pip install -r requirements.txt
```

##### Quickstart:
```
a = aud.Dir("folder", ['wav', 'mp3'], logfile="main.log")

a.log("Backing up")
a.backup("backups/todays_date/")

a.log("Changing filenames to all uppercase")
a.name_upper()

a.log("Creating exports for Amuse")
a.export_for("amuse", "exports/amuse")

a.log("add initials to all files")
a.name_append("_ZH")

a.log("Zip files up")
a.zip("my_files.zip")
```
