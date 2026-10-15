# Metadata naming profiles

`NamingProfile` renders a directory tree and filename from canonical metadata.
It changes paths only: audio bytes, artwork, and tags are not rewritten.
Unicode is preserved and normalized to NFC by default. Profiles are ordinary
Python configuration and do not depend on a particular community's conventions.

```python
from aud import Dir, NamingProfile

d = Dir("album", extensions=["flac"])
profile = NamingProfile(
    directory="{album_artist} - {album} ({year}) [{encoding_profile}]/Disc {disc_number:02}",
    filename="{track_number:02} - {title}",
    defaults={"encoding_profile": "FLAC", "disc_number": 1},
)
plan = d.plan_naming(profile, "organized", copy=True)
print(d.preview(plan).to_dict())
result = d.execute(plan, continue_on_error=True)
```

The example explicitly supplies a single-disc fallback and a label appropriate
to its FLAC selection. Supply these only when they describe the selected files.
The library does not infer edition, source, or encoding history from filenames.
`copy=True` leaves original files intact; the default moves them after publishing
each destination. Successful outputs become the selection. Empty source folders
are retained. This operation is not a complete album/sidecar package exporter.

`plan_naming()` reads tags with the bounded FFmpeg probe and snapshots canonical
metadata. Preparing the plan does not write anything. `Dir.preview()` then checks
all fields, paths, and collisions without writes, using that snapshot rather than
re-probing. Execution repeats preflight; a preview is not a filesystem reservation.
To avoid probes or correct metadata explicitly, provide a complete mapping:

```python
from aud import AudioMetadata

plan = d.plan_naming(
    NamingProfile(directory="", filename="{track_number:02}-{title}"),
    "organized",
    metadata={
        "original.flac": AudioMetadata.from_tags({"track": "1/10", "title": "Example"}),
    },
    copy=True,
)
```

Relative metadata keys are relative to `d.directory`; absolute keys also work.
When a mapping is supplied, it replaces probing entirely. Missing mapping entries
are missing metadata. Canonical fields are `artist`, `album_artist`, `album`,
`title`, `year`, `track_number`, `track_total`, `disc_number`, and `disc_total`.
Other fields, such as `source`, `edition`, `catalog_number`, or `encoding_profile`,
must be explicitly supplied in `defaults`. Metadata values take precedence over
fallback defaults. `AudioMetadata.issues` must be resolved before naming; missing
artist/year/disc values are never fabricated. See [the metadata contract](AUDIO_CHAINS.md).

`missing="error"` stops preflight on a missing field. `missing="skip"` records a
skipped file and retains its source in the selection. Invalid or ambiguous metadata
and invalid paths still fail; skipping is not permission to ignore validation.
`d.name_profile(profile, output_directory, metadata=..., copy=True)` is the boolean
convenience method and wraps failures as `FilenameError`.

Templates accept named fields and numeric widths from 1 to 9, such as
`{track_number:02}`, `{disc_number:02d}`, or `{year:04}`. `{{` and `}}` escape braces.
Attribute/index access, conversions such as `!r`, nested formats, expressions,
and unknown fields are rejected. Directory templates use `/` between at most
16 components. They must be relative and cannot include empty, `.` or `..`
components, drive prefixes, backslashes, or literal colons. Filename templates
have one component; the original extension is appended in lowercase.

Profile transformations apply to directory components and the filename stem:

- `case="preserve"`, `"upper"`, or `"lower"`.
- `space_replacement`, containing 1-8 spaces, dots, underscores, or hyphens.
- `ascii_only=True` for NFKD ASCII folding. This drops unsupported characters;
  it is not general transliteration or romanization. Review the preview carefully.
- Literal `prefix` and `suffix` for the filename stem.

For example, `NamingProfile(directory="{album}", filename="{track_number:02}-{title}",
case="upper", ascii_only=True, space_replacement="_")` provides uppercase ASCII
names with underscores. Original tags remain available and unchanged.

Metadata cannot introduce subdirectories: slashes, backslashes, Windows-forbidden
characters, controls, formatting controls, and surrogates become underscores.
Whitespace runs use the chosen replacement; leading/trailing spaces and dots are
trimmed. Reserved Windows device names receive an underscore prefix. Empty names
fail. Components, including the final extension, must fit both 255 UTF-8 bytes
and 255 UTF-16 code units; oversized names fail instead of being truncated.
Templates/affixes and individual field inputs are limited to 4096 characters.
These component rules do not guarantee every filesystem's whole-path limit.

Collisions are checked after transformation using NFC and case folding on every
OS. Existing `error`, `skip`, `overwrite`, and `auto-rename` policies apply. An
overwrite cannot consume another selected input or duplicate planned destination.
Directory spelling aliases and file/directory prefix conflicts fail preflight.
Symlink/reparse outputs are rejected. A same-key in-place operation must identify
the same parent directory; case/Unicode equality alone cannot imply a no-op.

The caller chooses the output root; relative roots use the process working
directory. Generated paths remain under that root. This is not an OS sandbox.
Existing staging, per-file results, failure dependencies, and between-file
cancellation apply. Completed outputs remain after later failures. Concurrent
source/ancestor replacement, crash rollback, and atomic whole-album moves are
outside the [safe processing guarantees](SAFE_PROCESSING.md).

For filename-derived candidate metadata, use the explicit
[filename parsing API](FILENAME_PARSING.md). Parsed values are not merged with
tags automatically and do not rewrite source metadata.

For custom multi-step plans, `NameWithProfile` is available from
`aud.core.operations.naming`. Its metadata keys must match the paths reaching that
step, including earlier copies/conversions. It does not infer tag changes from
prior operations or probe future output paths. Prefer preparing `plan_naming()`
after conversion when naming should use the converted file's actual tags.

References: [Windows naming rules](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file),
[Python format syntax](https://docs.python.org/3/library/string.html#format-string-syntax).
