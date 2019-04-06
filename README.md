# aud

## Quick tools for an audio studio environment

### Functionality:
  import aud

  file = AudFile(filepath)
  dir = AudDir(filepath, extensions=['wav', 'mp3'])

  file.help()
  dir.help()
    prints out examples of all commands

  dir.setExtensions(['wav', 'mp3', 'ogg'])
    select which extensions to apply commands to within a directory

  dir.setOutputDir(dirpath)
    select which directory to output to

  file.convert(target_samplerate=44100, target_bitdepth=16)
  dir.convert(target_samplerate=44100, target_bitdepth=16)
    converts all audio files to a specific file type, sample rate, and bit depth
    uses FFMPEG for high quality conversions

  file.pad(lead=0.0, trail=0.0)
  dir.pad(lead=0.0, trail=0.0)
    add leading or trailing space

  file.fade(in=0.0, out=0.0, type='log|lin', ratio=0.0)
  dir.fade(in=0.0, out=0.0, type='log|lin', ratio=0.0)
    add fades in and out of tracks

  file.prepend(prefix="", numbered=False, padding=2)
  dir.prependAll(prefix="", numbered=False, padding=2)
    prepend to file name like 02_prefix_filename

  file.upper()
  dir.upper()
    make file name uppercase

  file.lower()
  dir.lower()
    make file name lowercase

  file.replaceSpace()
  dir.replaceSpace()
    replace spaces with underscores

  file.move(target_dirpath)
  dir.move(target_dirpath)
    move audio files

  file.metadata(tags=["Artist Name": "Rei Harakami"])
  dir.metadata(tags=["Artist Name": "Nobukazu Takemura", "Type": "sfx", "Keywords": "short oneshot upbeat"])
    add metadata to a file. use common fields or make up your own to help batch categorize all of those new samples!

  dir.log(meta=['samplerate', 'bitdepth', 'length', 'size', 'tags'], format='txt')
    log all files with metadata to txt
    uses the set params and overwrites old log
    txt, csv, json

    >> Add metadata tags
