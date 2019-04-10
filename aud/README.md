# aud - Quick tools for an audio studio environment

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

#### Rename a file to replace_spaces_with_underscores
```python
>> dirpath.renameReplaceSpaces()
>> filepath.renameReplaceSpaces()
```

#### Add leading and/or trailing space for an audio file
```python
>> dirpath.pad(_in = 2.0, _out = 3.5)
>> filepath.pad(_out = 2.2)
```

#### Convert a file to a particular format
```python
>> dirpath.convertTo(_extension=".wav", _target_samplerate=44100, _target_bitdepth=16)
>> filepath.convertTo(_extension=".mp3", _target_samplerate=44100, _target_bitrate="320k") #bitrate="0" for lossy compression
```
