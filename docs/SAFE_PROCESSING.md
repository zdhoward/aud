# Safe processing contract

This implementation slice preserves existing boolean convenience methods and
allowlist override behavior. New options are keyword-only: `overwrite` defaults
to `error`, `follow_symlinks` defaults to false, and `pattern` narrows the selection
with a filename glob. A bare `Dir` still selects nothing for compatibility.

Collision policies are `error`, `skip`, `overwrite`, and `auto-rename` (a numeric
suffix). Preflight resolves all destinations before any file is changed. It
rejects writes over another selected input, including mixed-format conversions.
Unicode-normalized, case-folded names are considered collisions on every OS.
Explicit in-place effects and same-format conversions remain supported.

Writes use uniquely owned staging files beside their destinations. Failed writes
remove only staging files. New destinations are published with Windows' exclusive
rename or a POSIX exclusive hard link, so a destination appearing after preflight
cannot be overwritten. POSIX filesystems without hard-link support fail safely
rather than falling back to unsafe writes.
Explicit replacements use `os.replace`. Moving deletes the source only after
publishing the destination. A batch is not a transaction: completed outputs remain
after a later failure, and results identify them. Crash durability, rollback, and
hostile concurrent replacement of ancestor directories are not guaranteed.
Source files must not be edited or replaced concurrently during processing.

Scanning skips symbolic links and Windows reparse points by default. Opt-in link
selection resolves files to their actual paths. Destination links and reparse
ancestors are rejected. Caller-selected output directories may be outside the
working directory; this library is not an OS sandbox.

`Dir.plan()` snapshots the selection. `Dir.preview(operation_or_plan)` resolves
destinations and collision decisions without writes. `Dir.execute(plan)` returns
structured outcomes; `continue_on_error=True` permits independent files to continue.
Existing methods raise typed errors and leave the partial outcome in `last_result`.
Plans containing joins/archives explicitly describe a grouped operation. Preview
is an inspection snapshot, not a reservation against external filesystem changes.
Cancellation through `execute(..., cancel=event.is_set)` stops between files
and during active direct-FFmpeg conversions. pydub effects stop between files.
Plans that would reuse a still-existing original destination are conservatively
rejected; arbitrary rename cycles and batch rollback are not supported.

Audio exports are staged and decoded to validate format before publication. Raw
PCM is validated by byte length because it has no self-describing header. Preserve
ordinary source tags and the nominal MP3 bitrate for in-place effects. Full artwork,
custom tag mappings, and VBR preset identity remain limitations for effects.
Direct conversions support sample-exact 24-bit PCM and MP3/FLAC artwork; see the
[FFmpeg conversion contract](FFMPEG_CONVERSION.md).

Implementation references: [Python filesystem operations](https://docs.python.org/3/library/os.html),
[secure temporary creation](https://docs.python.org/3/library/tempfile.html), and
[subprocess security considerations](https://docs.python.org/3/library/subprocess.html#security-considerations).
