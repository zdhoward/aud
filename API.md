# aud API

### Getting Started
```
from aud import Dir
a = Dir(directory)
```

##### Core Operations
```
a.get_all()
a.get_single()
a.backup(target_directory)
a.move(target_directory)
a.copy(target_directory)
a.zip(target_location, format, options[])
a.log(msg)
```

##### Config
```
a.config_get_allowlist()
a.config_set_allowlist(list) # should accept regex too
a.config_get_denylist()
a.config_set_denylist(list) # should accept regex too
a.config_set_log_file(target_location)
a.config_set_extensions(extensions[])
a.config_get_extensions()
```
##### File Name Operations
```
a.name_upper()
a.name_lower()
a.name_iterate(zerofill=0, separator="_")
a.name_prepend(string)
a.name_append(string)
a.name_replace(target, replacement)
a.name_replace_spaces(replacement="_")
```
##### Audio FX Operations:
```
a.afx_normalize(target_level=0.1, passes=1)
a.afx_fade(in_fade, out_fade)
a.afx_pad(in_pad, out_pad)
a.afx_watermark(watermark_file, frequency_min, frequency_max)
a.afx_join(target_location, format="wav")
a.afx_prepend(file)
a.afx_append(file)
a.afx_strip_silence(silence_length=1000, silence_threshold=-16, padding=100)
a.afx_invert_stereo_phase(channel="both") ## accepts left, right, and both
a.afx_lpf(cutoff)
a.afx_hpf(cutoff)
a.afx_gain(amount)
```

##### Conversion Operations:
```
a.convert_to_mono()
a.convert_to_stereo()
a.convert_to_wav(sample_rate=None, bit_depth=None, cover=None)
a.convert_to_mp3(bit_rate=None, bit_depth=None, cover=None, tags=None)
a.convert_to_flac(sample_rate=None, bit_depth=None, cover=None, tags=None)
a.convert_to_raw(sample_rate=None, bit_depth=None, cover=None)
a.convert_to(format="wav", sample_rate=None, bit_depth=None, cover=None, tags=None)
```

##### Export For Platform:
```
a.export_for(self, target_platform, target_directory)
```

##### Things to come:
```
a.vfx_overlay_image(image)
```
