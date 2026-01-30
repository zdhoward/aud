# aud API Reference

## Getting Started

```python
from aud import Dir

# Create a Dir instance for a directory
d = Dir("path/to/directory")

# Or with initial configuration
d = Dir(
    "path/to/directory",
    extensions=["wav", "mp3"],
    allowlist=["song1.wav", "song2.mp3"],
    denylist=["ignore.wav"]
)
```

## Core Operations

### File Information
```python
# Get list of all selected file names
d.get_all()  # Returns: list[str]

# Get number of selected files
len(d)  # Returns: int

# Iterate over selected files
for file in d:
    print(file)  # AudioFile object
```

### File Operations
```python
# Copy files to target directory
d.copy(target_directory)

# Move files to target directory
d.move(target_directory)

# Backup files to target directory (alias for copy)
d.backup(target_directory)

# Create zip archive of selected files
d.archive_zip("output.zip")
```

## Configuration

### Extensions
```python
# Set allowed file extensions
d.config_set_extensions(["wav", "mp3", "flac"])

# Get current extensions
d.config_get_extensions()  # Returns: list[str]
```

### Allowlist / Denylist
```python
# Set allowlist (specific filenames or regex pattern)
d.config_set_allowlist(names=["song1.wav", "song2.mp3"])
d.config_set_allowlist(regex=r"^song_\d+\.wav$")

# Set denylist (specific filenames or regex pattern)
d.config_set_denylist(names=["temp.wav", "test.mp3"])
d.config_set_denylist(regex=r"^temp_.*")
```

### Log File
```python
# Set log file location (currently not used by core operations)
d.config_set_log_file("operations.log")
```

## File Name Operations

```python
# Convert all filenames to uppercase
d.name_upper()

# Convert all filenames to lowercase
d.name_lower()

# Add prefix to filenames
d.name_prepend("prefix_")

# Add suffix to filenames (before extension)
d.name_append("_suffix")

# Replace text in filenames
d.name_replace("old_text", "new_text")

# Replace spaces with another character
d.name_replace_spaces("-")  # Default: "_"

# Add sequential numbers to filenames
d.name_iterate(zerofill=2, separator="_")
# Example: file.wav -> 01_file.wav, 02_file.wav, ...
```

## Audio Effects Operations

All audio effects are applied in-place to the selected files.

```python
# Normalize audio levels
d.afx_normalize(target_level=0.1, passes=1)
# target_level: headroom in dB (default: 0.1)
# passes: number of normalization passes (default: 1)

# Apply fade in/out
d.afx_fade(in_fade=1.0, out_fade=2.0)
# in_fade: fade in duration in seconds
# out_fade: fade out duration in seconds

# Add silence padding
d.afx_pad(in_pad=0.5, out_pad=0.5)
# in_pad: silence duration at start in seconds
# out_pad: silence duration at end in seconds

# Adjust gain/volume
d.afx_gain(amount_db=3.0)
# amount_db: gain adjustment in decibels (positive = louder, negative = quieter)

# Apply low-pass filter
d.afx_low_pass(cutoff_hz=5000)
# cutoff_hz: cutoff frequency in Hz

# Apply high-pass filter
d.afx_high_pass(cutoff_hz=100)
# cutoff_hz: cutoff frequency in Hz

# Invert stereo phase
d.afx_invert_phase(channel="both")
# channel: "both", "left", or "right"
```

## Conversion Operations

Conversion operations modify the audio format or channel configuration.

```python
# Convert to mono (single channel)
d.convert_mono()

# Convert to stereo (two channels)
d.convert_stereo()

# Convert to different format
d.convert_format(
    target_format="mp3",
    sample_rate=44100,      # Optional: target sample rate in Hz
    bit_depth=16,           # Optional: target bit depth (8, 16, 24, or 32)
    tags={"artist": "Name", "album": "Album"},  # Optional: metadata tags
    cover="cover.jpg"       # Optional: album art file path
)

# Supported formats: wav, mp3, flac, ogg
```

### Conversion Examples

```python
# Convert to WAV at 44.1kHz, 16-bit
d.convert_format("wav", sample_rate=44100, bit_depth=16)

# Convert to MP3 with metadata
d.convert_format(
    "mp3",
    tags={
        "artist": "Artist Name",
        "album": "Album Title",
        "title": "Song Title"
    }
)

# Convert to FLAC with high quality
d.convert_format("flac", sample_rate=48000, bit_depth=24)
```

## Export for Platform

```python
# Export files for specific platform (basic implementation)
d.export_for(target_platform="wav", target_directory="export")
d.export_for(target_platform="mp3", target_directory="export")

# Currently supported platforms: wav, mp3
# More platforms planned for future releases
```

## Selection Behavior

The `Dir` class uses a policy-based selection system:

1. **Extensions**: If extensions are set, only files with matching extensions are included
2. **Denylist**: Files matching denylist (names or regex) are excluded
3. **Allowlist**: Files matching allowlist (names or regex) are always included, overriding other rules

The selection is evaluated as: `(valid_extension AND NOT denylisted) OR allowlisted`

After any configuration change (`config_set_*`), the file selection is automatically updated via `update()`.

## Error Handling

All operations raise specific exceptions on failure:

- `FilenameError`: File naming operations failed
- `FileError`: File operations (copy/move/backup/zip) failed
- `AudioFXError`: Audio effects operations failed
- `ConvertError`: Conversion operations failed
- `ExportError`: Export operations failed

```python
from aud.exceptions import AudioFXError

try:
    d.afx_normalize()
except AudioFXError as e:
    print(f"Normalization failed: {e}")
```

## Return Values

Most operations return `bool`:
- `True`: Operation completed successfully
- Raises exception on failure

Configuration getters return their respective values:
- `get_all()`: `list[str]`
- `config_get_extensions()`: `list[str]`

## Notes

- All operations are applied to the currently selected files
- File selection can be modified at any time using `config_set_*` methods
- Operations modify files in-place unless using `copy()`, `move()`, or `backup()`
- The `update()` method is called automatically after configuration changes
