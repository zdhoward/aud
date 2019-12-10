# aud
### v0.8.0
[![CircleCI](https://circleci.com/gh/zdhoward/aud.svg?style=svg)](https://circleci.com/gh/zdhoward/aud)

- Support for Python 3.8
- Support for Windows & Ubuntu
- Requires ffmpeg is already installed and updated

##### To start contributing:
```
>> git clone https://github.com/zdhoward/aud-rework.git
>> cd aud-rework
>> virtualenv venv
>> python3 -m pip install -r requirements.txt
```

##### Getting Started
```
from aud import Dir

[T] a = Dir(directory)
```

##### Core Operations
```
[T] a.get_all()
[T] a.get_single()
[T] a.backup(target_directory)
[T] a.move(target_directory)
[T] a.copy(target_directory)
[T] a.zip(target_location, format, options[])
[T] a.log(msg)
```

##### Config
```
[T] a.config_get_whitelist()
[T] a.config_set_whitelist(list) # should accept regex too
[T] a.config_get_blacklist()
[T] a.config_set_blacklist(list) # should accept regex too
[T] a.config_set_log_file(target_location)
[T] a.config_set_extensions(extensions[])
[T] a.config_get_extensions()
```
##### File Name Operations
```
[T] a.name_upper()
[T] a.name_lower()
[T] a.name_iterate(zerofill, seperator)
[T] a.name_prepend(string)
[T] a.name_append(string)
[T] a.name_replace(target, replacement)
[T] a.name_replace_spaces(replacement)
```
##### Audio FX Operations:
```
[T] a.afx_normalize(target_level, passes)
[T] a.afx_fade(in_fade, out_fade)
[T] a.afx_pad(in_pad, out_pad)
[T] a.afx_watermark(file, frequency_min, frequency_max)
[T] a.afx_join(files[])
[T] a.afx_prepend(file)
[T] a.afx_append(file)
[T] a.afx_strip_silence(silence_length, silence_threshold, padding)
[T] a.afx_invert_stereo_phase('left') ## accepts left, right, and both
[T] a.afx_lpf(cutoff)
[T] a.afx_hpf(cutoff)
[T] a.afx_mono_gain(amount)
[T] a.afx_stereo_gain(amount)
```

##### Conversion Operations:
```
[T] a.convert_to_mono()
[T] a.convert_to_stereo()
[T] a.convert_to_wav(sample_rate)
[T] a.convert_to_mp3(bit_rate)
[T] a.convert_to_flac()
[T] a.convert_to_raw()
[T] a.convert_to(format)
```

##### Things to come:
```
[ ] a.vfx_overlay_image(image)
```
