# aud - Quick tools for an audio studio environment

aud is an audio package meant to help streamline batch audio edits.
It allows you to easily work with complex file structures and naming conventions.
It is also meant to be easy enough for a beginner programmer to dive in and use.
The foundation of this package relies on two core pieces; FFMPEG and PyDub.

AudDir allows you perform batch audio actions on messy folders. 
When working with audio you may often end up with many arbitrary files your DAW may produce so AudDir allows you to point only to specific extensions in a directory and to work with them on the fly.

```
Requirements:
>> python3
>> ffmpeg
>> ffmpeg-normalize
```

Make sure all of the requirements are installed to your $PATH before use

#### Import The Package:
```python
>> import aud
```

#### AudFile
```python
>> filepath = aud.AudFile("test.wav")
```

#### AudDir
```python
>> dirpath = aud.AudDir("test")
```

#### Set which file types in the directory to effect
```python
>> dirpath.extensions = [".wav", ".mp3"]
```

#### For commands that change more than the name of an audio file, set the output folder
```python
>> dirpath.setOutputDir("_Processed")
```

#### Generate a log file for a particular directory
```python
>> dirpath.log("_Processed")
```

#### Add metadata tags to a file. There are standards but you can make up your own
```python
>> dirpath.metadata(["Artist": "Nobukazu Takemura", "Type": "sfx", "Keywords": "sword oneshot stereo"])
>> filepath.metadata(["Artist": "Rei Harakami", "Project": "Game Jam", "Keywords": "loop bgm"])
```

#### Rename a file to be all lowercase
```python
>> dirpath.renameLower()
>> filepath.renameLower()
```

#### Rename a file to be all UPPERCASE
```python
>> dirpath.renameUpper()
>> filepath.renameUpper()
```

#### Rename a file to prepend a string
```python
>> dirpath.renamePrepend("bgm_loop_")
>> filepath.renamePrepend("sword_sfx_")
```

#### Rename files to prepend iterated numbers with variable zerofill
```python
>> dirpath.renameIterate(3)
```

#### Rename a file to replace_spaces_with_underscores
```python
>> dirpath.renameReplaceSpaces()
>> filepath.renameReplaceSpaces()
```

#### Move audio files
```python
>> dirpath.move("C://Share/Audio")
>> filepath.move("/mnt/share")
```

#### Add leading and/or trailing space for an audio file
```python
>> dirpath.pad(_in = 2.0, _out = 3.5)
>> filepath.pad(_out = 2.2)
```


#### Add fade in or out for an audio file in seconds
```python
>> dirpath.fade(_in = 5.0, _out = 10.5)
>> filepath.fade(_out = 2.2)
```

#### Normalize audio
```python
>> dirpath.normalize()
>> dirpath.normalize(_type="peak")
>> filepath.normalize(_type="peak", _target=-6)
```

#### Convert a file to a particular format
```python
>> dirpath.convertTo(_extension=".wav", _target_samplerate=44100, _target_bitdepth=16)
>> filepath.convertTo(_extension=".mp3", _target_samplerate=44100, _target_bitrate="320k") #bitrate="0" for lossy compression
```
