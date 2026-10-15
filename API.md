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

# Get a single file name by index (negative indices allowed)
d.get_single(0)  # Returns: str
# Out-of-range indices raise IndexError
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

Unreleased metadata-based naming uses `NamingProfile`, `Dir.plan_naming()`, and
`Dir.name_profile()`. It supports directory/filename templates, disc-aware numbers,
case/spacing/ASCII options, explicit defaults, and missing-field policies. See
[naming profiles](docs/NAMING_PROFILES.md) for copy/move examples and portability
limits. Preparation snapshots supplied or probed metadata; preview and execution
validate all destinations before writes. Naming preserves audio bytes and tags.

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
    bit_depth=16,            # Optional: WAV/raw 8/16/24/32; FLAC 16/24
    bit_rate=192,            # Optional: encoder bitrate in kbps (lossy formats only)
    tags={"artist": "Name", "album": "Album"},  # Optional: metadata tags
    cover="cover.jpg"        # Optional: album art file path
)

# Supported formats: wav, mp3, flac, ogg
```

### Conversion Examples

```python
# Convert to WAV at 44.1kHz, 16-bit
d.convert_format("wav", sample_rate=44100, bit_depth=16)

# Convert to MP3 with metadata at 192 kbps
d.convert_format(
    "mp3",
    bit_rate=192,
    tags={
        "artist": "Artist Name",
        "album": "Album Title",
        "title": "Song Title"
    }
)

# Convert to FLAC at 48kHz, 16-bit
d.convert_format("flac", sample_rate=48000, bit_depth=16)
```

## Export for Platform

```python
# Export files for a platform preset (converted copies are written to
# target_directory; source files and the current selection are untouched)
d.export_for(target_platform="cd", target_directory="export")

# Supported platforms:
# - "amuse": WAV 44.1kHz 16-bit
# - "cd":    WAV 44.1kHz 16-bit
# - "wav":   WAV (source sample rate/bit depth preserved)
# - "mp3":   MP3
# Unsupported platforms raise ExportError.
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

### Safe execution and inspection

`Dir(..., overwrite="error", follow_symlinks=False, pattern=None)` adds
keyword-only safety options. Overwrite policies are `error`, `skip`, `overwrite`,
and `auto-rename`. `pattern` is a filename glob intersected with the existing
selection. Allowlists retain their documented override behavior.

```python
from aud import Dir
from aud.core.operations.files import Copy

d = Dir("masters", extensions=["wav"], pattern="final_*.wav")
plan = d.plan().add(Copy("exports"))
print(d.preview(plan).to_dict())
result = d.execute(plan, continue_on_error=True)
print(result.to_dict())
```

Preview resolves collisions without writes and raises if the plan is unsafe.
Execution recomputes the preview snapshot, then uses those resolved destinations
without selecting files again. `last_result` records `success`, `skipped`,
`failed`, `not_run`, or `cancelled` outcomes, including partial completion before
a legacy method raises. New `execute` calls raise underlying errors by default;
`continue_on_error=True` continues independent files and returns a false-valued
result if any file failed. Cancellation accepts `cancel=event.is_set` and stops
between files or during an active conversion. Batches are not atomic transactions.

Sources remain unchanged if export/validation fails before publication. Ordinary
MP3/FLAC tags and nominal MP3 bitrates are retained by in-place processing; full
artwork and VBR preset preservation for effects are still pending. See
[the safe processing contract](docs/SAFE_PROCESSING.md) for filesystem and
concurrency limits.

### Direct conversion and encoding profiles (unreleased)

`AudioChain` groups supported effects and an optional conversion into one final
encode per file. `Dir.afx_chain(effects, output=conversion)` is the boolean helper;
`Dir.execute(plan.add(AudioChain(...)))` provides results and cancellation. See
[the chain and metadata contract](docs/AUDIO_CHAINS.md) for examples and supported
effects. `AudioChain` and `AudioMetadata` are exported from `aud`.

```python
from aud import Dir, MediaLimits
from aud.core.operations.audio.convert import ConvertFormat

d = Dir("masters", extensions=["wav", "flac"],
        media_limits=MediaLimits(timeout=600, output_bytes=2 * 1024**3))
plan = d.plan().add(ConvertFormat(
    "mp3", profile="mp3-v0", output_directory="deliverables",
    tags={"album": "Example"},
))
print(d.preview(plan))
result = d.execute(plan, continue_on_error=True)
print(result.to_dict())
```

`convert_format()` accepts the same keyword-only `output_directory`, `profile`,
`allow_lossy`, `drop_artwork`, and `channels` options. Profiles are `flac-preserve`,
`mp3-v0`, `mp3-v2`, and `mp3-320`; they require visibly lossless input unless
`allow_lossy=True`. Do not combine a profile with an explicit `bit_rate`.
Relative output paths resolve from the process working directory. Conversion
updates the selection to successful outputs; `export_for()` keeps its source selection.

Conversions retain ordinary container/audio-stream tags and MP3/FLAC attached
artwork. Container tags win over matching stream tags; explicit tags win over
both. Unsupported artwork requires explicit `drop_artwork=True`. Successful
`FileResult.details` records effective encoder/profile/sample properties and
`unmapped_tags`, including metadata the target cannot represent. Raw PCM carries
no tags. Probe, encode, and verification each have their own `MediaLimits`
deadline; limits are polled application controls. See the
[conversion contract](docs/FFMPEG_CONVERSION.md) for validation and security limits.

Details also include canonical `source_metadata` and `output_metadata`, with
nullable fields, original tags, and parsing issues. This read-only view supports
explicit future naming templates without deriving artist/year from filenames.

Most operations return `bool`:
- `True`: Operation completed successfully (including no-op on an empty selection)
- Raises exception on failure

Configuration getters return their respective values:
- `get_all()`: `list[str]`
- `config_get_extensions()`: `list[str]`

## Notes

The unreleased console interface wraps these APIs; see [CLI usage](docs/CLI.md)
for command selection, JSON configuration, dry runs, and exit codes.

Unreleased album preparation uses `plan_album(target, *, service="generic",
release, metadata=None, track_order=None, **options) -> AlbumPackage`,
`preview(package) -> AlbumPreview`, and `execute(package) -> BatchResult`.
`package_album()` combines these steps. Options include `artwork`, `sidecars`,
`default_disc`, `audio_format`, `allow_audio_changes`, `allow_lossy`, and `naming`.
Preparation and execution accept `cancel`; the convenience method and execution
also accept `continue_on_error`. Sources and selection stay intact.
Public `DELIVERY_PROFILES` and `delivery_profile(name)` expose versioned settings.
See the [contract and examples](docs/ALBUM_PACKAGING.md) for path resolution,
metadata requirements, supported services, resource limits, and manual review.

- All operations are applied to the currently selected files
- File selection can be modified at any time using `config_set_*` methods
- Operations modify files in-place unless using `copy()`, `move()`, or `backup()`
- `Dir()` raises `FileNotFoundError` if the given path is not an existing directory
- The `update()` method is called automatically after configuration changes
