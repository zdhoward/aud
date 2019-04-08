import aud

logger = setupLogger()

dirpath = aud.AudDir("test")
dirpath.pad(2.0, 3.5)
dirpath.renameUpper()
dirpath.renameLower()
dirpath.log()
dirpath.metadata(["Artist": "Nobukazu Takemura", "Type": "sfx", "Keywords": "sword oneshot stereo"])

dirpath.convertTo(_extension=".wav", _target_samplerate=44100, _target_bitdepth=16)

filepath = aud.AudDir("test.wav")
filepath.renameReplaceSpaces()
filepath.renamePrepend("sword_sfx_")

logger.debug(filepath)
# C:\Folder\test.wav
