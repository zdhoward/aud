# aud

## Quick tools for an audio studio environment

### Functionality:
  from aud import AudFile, AudDir

  file = AudFile(filepath)
  dir = AudDir(filepath, extensions=['wav', 'mp3'])

  file.help()
  dir.help()
    prints out examples of all commands

  dir.setExtensions(['wav', 'mp3', 'ogg'])
    select which extensions to apply commands to within a directory

  file.convert()
  dir.convert()
    converts all audio files to a specific file type, sample rate, and bit depth
    uses FFMPEG for high quality conversions


>>
>>  import aud
>>  # utility audio tools for a fast paced studio-life
>>  # make it live interpreter friendly
>>
>>  # print examples of each command
>>  aud.help()
>>
>>  # allow input folder for batch processes
>>  aud.setInputFolder(filepath)
>>
>>  # set output folder to offer flexibility
>>  # default to same folder
>>  aud.setOutputFolder(filepath='_Processed')
>>
>>  # select extensions to target
>>  # default to wav
>>  aud.setExtensions(["mp3", "wav", "ogg"])
>>
>>  # add leading or trailing space
>>  aud.pad(filepath, lead=0.0, trail=0.0)
>>  aud.padAll(dirpath, lead=0.0, trail=0.0)
>>
>>  # add fades
>>  aud.fade(filepath, in=0.0, out=0.0, type='log|lin', ratio=0.0)
>>  aud.fadeAll(dirpath, in=0.0, out=0.0, type='log|lin', ratio=0.0)
>>
>>  # prepend to file name like 02_prefix_filename
>>  aud.prepend(filepath, prefix="", numbered=False, padding=2)
>>  aud.prependAll(dirpath, prefix="", numbered=False, padding=2)
>>
>>  # convert to particular format
>>  aud.convert(filepath, targetFormat="wav", samplerate=44100, bitdepth=16)
>>  aud.convertAll(dirpath, targetFormat="wav", samplerate=44100, bitdepth=16)
>>
>>  # make file name uppercase
>>  aud.upper(filepath)
>>  aud.upperAll(dirpath)
>>
>>  # make file name lowercase
>>  aud.lower(filepath)
>>  aud.lowerAll(dirpath)
>>
>>  # replace spaces with underscores
>>  aud.replaceSpace(filepath)
>>  aud.replaceSpaceAll(dirpath)
>>
>>  # move audio files
>>  aud.move(source_filepath, target_dirpath)
>>  aud.moveAll(source_dirpath, target_dirpath)
>>
>>  # may be overextending, needlessly adding external programs, zipfile, rarfile
>>  # pack file as rar, zip, or 7zip. lossless/no compression. password possible.
>>  aud.pack(filepath, type='rar', password='')
>>  aud.packAll(dirpath, type='rar', password='')
>>
>>  # log all files with metadata to txt
>>  # uses the set params and overwrites old log
>>  # txt, csv, json
>>  aud.log(meta=['samplerate', 'bitdepth', 'length', 'size', 'tags'], format='txt')
>>
>>  # add metadata for tags like 'sfx' or 'sword'
