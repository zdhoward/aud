import aud

logger = setupLogger()

dirpath = aud.AudDir("test")

dirpath.extensions = [".wav", ".mp3"]

dirpath.setOutputDir("_Processed")

dirpath.metadata(["Artist": "Nobukazu Takemura", "Type": "sfx", "Keywords": "sword oneshot stereo"])

dirpath.renameUpper()

dirpath.renameLower()

dirpath.pad(_in=2.0, _out=3.5)

dirpath.log("_Processed")

dirpath.convertTo(_extension=".wav", _target_samplerate=44100, _target_bitdepth=16)

filepath = aud.AudDir("test.wav")

filepath.renameReplaceSpaces()

filepath.renamePrepend("sword_sfx_")

filepath.convertTo(_extension=".mp3", _target_samplerate=44100, _target_bitrate="320k") #bitrate="0" for lossy compression

logger.debug(filepath)
# C:\Folder\test.wav
