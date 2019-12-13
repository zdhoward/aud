# aud Examples

##### Exporting a whole directory of mp3s for Amuse
```
from aud import Dir
a = Dir("/home/my_folder/", extensions=["mp3"])
a.export_for("amuse", "/home/exports/amuse")
```

##### Forcing uppercase, prepending numbers, and appending initials
```
from aud import Dir
a = Dir("this_folder")
a.name_upper()
a.name_iterate(zerofill=2, separator="-")
a.name_append("_ZH")
```

##### Converting all files to a specific sample rate and bit depth
```
from aud import Dir
a = Dir("audio/project1")
a.convert_to_wav(sample_rate=44100, bit_depth=16)
```
