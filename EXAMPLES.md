# aud Examples

## Basic Usage

### Converting Audio Files to a Specific Format

```python
from aud import Dir

# Convert all MP3s in a directory to WAV at 44.1kHz, 16-bit
d = Dir("audio/source", extensions=["mp3"])
d.convert_format("wav", sample_rate=44100, bit_depth=16)
```

### Batch Renaming with Sequential Numbers

```python
from aud import Dir

# Add sequential numbers to files with zero-padding
d = Dir("samples")
d.name_iterate(zerofill=2, separator="-")
# Result: 01-file.wav, 02-file.wav, 03-file.wav, ...
```

### Standardizing File Names

```python
from aud import Dir

# Force uppercase, replace spaces, add prefix
d = Dir("audio/project")
d.name_upper()
d.name_replace_spaces("_")
d.name_prepend("TRACK_")
# Example: "my song.wav" -> "TRACK_MY_SONG.WAV"
```

## Audio Processing

### Normalizing Audio Levels

```python
from aud import Dir

# Normalize all WAV files in a directory
d = Dir("masters", extensions=["wav"])
d.afx_normalize(target_level=-0.5, passes=2)
```

### Adding Fade In/Out

```python
from aud import Dir

# Add 2 second fade in and 3 second fade out
d = Dir("audio")
d.afx_fade(in_fade=2.0, out_fade=3.0)
```

### Applying Filters

```python
from aud import Dir

# Remove frequencies below 80Hz (remove rumble)
d = Dir("recordings", extensions=["wav"])
d.afx_high_pass(cutoff_hz=80)

# Or remove frequencies above 10kHz
d.afx_low_pass(cutoff_hz=10000)
```

### Adjusting Volume

```python
from aud import Dir

# Increase volume by 6dB
d = Dir("quiet_tracks")
d.afx_gain(amount_db=6.0)

# Decrease volume by 3dB
d.afx_gain(amount_db=-3.0)
```

## File Management

### Organizing Audio Files

```python
from aud import Dir

# Copy all FLAC files to a backup directory
d = Dir("studio", extensions=["flac"])
d.backup("backups/studio_backup")
```

### Creating Archives

```python
from aud import Dir

# Create a ZIP archive of all project files
d = Dir("project_final", extensions=["wav", "mp3"])
d.archive_zip("archives/project_final.zip")
```

## Selection and Filtering

### Working with Specific Files

```python
from aud import Dir

# Only process files matching a pattern
d = Dir("mixed", extensions=["wav"])
d.config_set_allowlist(regex=r"^master_.*\.wav$")
d.afx_normalize()
```

### Excluding Files

```python
from aud import Dir

# Process all files except temporary ones
d = Dir("studio")
d.config_set_denylist(regex=r"^temp_.*")
d.config_set_denylist(names=["scratch.wav", "test.mp3"])
```

## Multi-Step Workflows

### Master Preparation Workflow

```python
from aud import Dir

# 1. Select only final mixes
d = Dir("project/mixes", extensions=["wav"])
d.config_set_allowlist(regex=r"^mix_final_.*\.wav$")

# 2. Normalize audio
d.afx_normalize(target_level=-0.3, passes=2)

# 3. Add fade out
d.afx_fade(out_fade=2.0)

# 4. Standardize naming
d.name_upper()
d.name_replace("MIX_FINAL_", "")
d.name_iterate(zerofill=2, separator="_")

# 5. Convert to distribution formats
d.backup("masters/wav")
d.convert_format("mp3", tags={"artist": "Artist Name", "album": "Album Title"})

# 6. Copy MP3s to distribution folder
d.copy("distribution/mp3")
```

### Batch Processing Multiple Directories

```python
from aud import Dir
from pathlib import Path

# Process multiple project directories
projects = ["project1", "project2", "project3"]

for project in projects:
    d = Dir(f"audio/{project}", extensions=["wav"])

    # Normalize and apply effects
    d.afx_normalize(target_level=-0.5)
    d.afx_high_pass(cutoff_hz=80)

    # Convert to MP3 and backup
    d.backup(f"processed/{project}/wav")
    d.convert_format("mp3")
    d.copy(f"processed/{project}/mp3")
```

### Sample Pack Preparation

```python
from aud import Dir

# Prepare samples for distribution
d = Dir("samples/raw", extensions=["wav"])

# 1. Clean up names
d.name_lower()
d.name_replace_spaces("_")
d.name_replace("sample_", "")

# 2. Standardize audio
d.convert_format("wav", sample_rate=44100, bit_depth=24)
d.afx_normalize(target_level=-1.0)

# 3. Add padding for clean loops
d.afx_pad(in_pad=0.01, out_pad=0.01)

# 4. Number sequentially
d.name_iterate(zerofill=3, separator="_")

# 5. Export to multiple formats
d.backup("sample_pack/wav")
d.convert_format("flac")
d.copy("sample_pack/flac")
```

## Format Conversion Examples

### Creating Distribution Masters

```python
from aud import Dir

# Start with high-quality WAV files
d = Dir("masters/wav", extensions=["wav"])

# Convert to FLAC for lossless distribution
d.convert_format("flac", sample_rate=48000, bit_depth=24)
d.copy("distribution/flac")

# Convert to MP3 for streaming
d = Dir("masters/wav", extensions=["wav"])
d.convert_format("mp3", tags={
    "artist": "Artist Name",
    "album": "Album Name",
    "year": "2024"
})
d.copy("distribution/mp3")
```

### Converting Legacy Formats

```python
from aud import Dir

# Convert old MP3s to modern high-quality format
d = Dir("old_library", extensions=["mp3"])
d.convert_format("flac", sample_rate=44100, bit_depth=16)
```

## Error Handling

```python
from aud import Dir
from aud.exceptions import AudioFXError, ConvertError, FileError

d = Dir("audio")

try:
    d.afx_normalize()
    d.convert_format("mp3")
    d.copy("output")
except AudioFXError as e:
    print(f"Audio processing failed: {e}")
except ConvertError as e:
    print(f"Conversion failed: {e}")
except FileError as e:
    print(f"File operation failed: {e}")
```

## Advanced Selection

### Processing Only Modified Files

```python
from aud import Dir
from datetime import datetime, timedelta

# Get all files
d = Dir("project")

# Filter to files modified in last 24 hours using allowlist
recent_files = [
    f.name for f in d
    if f.path.stat().st_mtime > (datetime.now() - timedelta(days=1)).timestamp()
]

d.config_set_allowlist(names=recent_files)
d.afx_normalize()
```

### Pattern-Based Processing

```python
from aud import Dir

# Process only stems (kick, snare, bass, etc.)
d = Dir("stems", extensions=["wav"])
d.config_set_allowlist(regex=r"^(kick|snare|bass|lead)_.*\.wav$")
d.afx_normalize()

# Process everything except effects
d = Dir("stems", extensions=["wav"])
d.config_set_denylist(regex=r"^(reverb|delay|fx)_.*\.wav$")
```
