# Command line interface (unreleased)

The base installation provides `aud`; no optional CLI dependencies are needed.
`python -m aud.cli` is equivalent. Run `aud --help`, `aud COMMAND --help`, or
`aud --version`. Commands use the same selection, overwrite, plans, previews,
and results as the Python API.

```shell
aud list masters --extensions wav flac --json
aud inspect masters --extensions wav --pattern "01*" --json
aud convert masters --extensions wav --format flac --profile flac-preserve --dry-run
aud export masters --extensions flac --format mp3 --profile mp3-v0 --output-directory listening --dry-run
aud rename masters --extensions wav --config naming.json --output-directory organized --copy --dry-run
aud effects masters --extensions wav --config effects.json --format flac --output-directory processed --dry-run
aud album masters --extensions wav --config album.json --target delivery/amuse.zip --service amuse --dry-run
```

Remove `--dry-run` to execute. Existing destinations fail unless you explicitly
choose `--overwrite skip`, `overwrite`, or `auto-rename`. There is no confirmation
prompt. Use `--continue-on-error` to attempt independent later files after an
execution failure; results still report failure. Do not rerun a partially
successful batch blindly: inspect its results and the new destinations first.

No files are selected without `--extensions`, matching the current Python API.
`--pattern` narrows that selection. Writes reject empty selections rather than
reporting a misleading successful batch. Scanning is nonrecursive and links are
skipped under the shared core policy. Use explicit `list ./album` when a directory
name matches a command. The earlier `aud DIRECTORY` count-only form remains
available, including its empty default selection; use `list` for useful output.

## Commands and output

Opt into versioned interchange with `--json --json-version 1`. See
[JSON contracts](JSON_CONTRACTS.md) for envelopes and compatibility; plain
`--json` is unchanged.

| Command | Behavior |
| --- | --- |
| `list` | Selected filenames, without decoding media. |
| `inspect` | Bounded ffprobe properties and original tags for selected files. |
| `convert` | A conversion plan; same-format conversion can replace its input in place under the core contract. |
| `export` | Conversion copies to a required output directory different from the source directory. Encoding profiles are shared with `convert`; distributor preparation uses `album`. |
| `rename` | A naming-profile plan; moves by default, copies with `--copy`. |
| `effects` | Ordered supported native effects, optionally with a final conversion. Without `--format`, effects replace source files in place. |
| `album` | A generic or service-specific local ZIP preparation plan. |

Human output is indented structured JSON with escaped path/tag strings.

Use `--progress` to print live file-level start/finish lines on stderr while
keeping stdout unchanged, including with `--json`. It is off by default. Counts
cover terminal decisions within the current adapter operation, including skipped,
failed, cancelled, and unattempted entries; they are not elapsed-time estimates.
Inspection reports each probe. Album payload events say `staged`; only the final
`AlbumPackage ... success` event indicates archive publication. Dry runs produce
no execution events. Preparation itself and progress within a long encode/copy
are not measured. Use the final result for authoritative outcomes.

`--json` emits one compact JSON document on stdout; human error diagnostics use
stderr. JSON errors include `succeeded: false`, `error`, `exit_code`, and `result`
(partial batch results when available). Successful execution uses the core
`BatchResult` shape; failed/cancelled non-throwing batches use that same shape.
Dry runs contain `dry_run: true` and `preview`. Help/version remain plain text.

| Exit code | Meaning |
| --- | --- |
| `0` | Successful read, preview, or batch (including explicitly skipped files). |
| `1` | Execution failure, including partial success. Legacy count-form errors also use 1. |
| `2` | Usage, configuration, selection, inspection, or preparation error before a recorded execution outcome. |
| `130` | Cancellation. |

Ctrl+C requests cancellation through the core callback. Running native media
processes are stopped and owned staging files cleaned; earlier committed files
remain reported. Preparation paths without active polling, including naming
metadata probing, can finish their current bounded call before cancellation is
observed. A final cancellation check prevents execution after preparation.
`--timeout` sets per-process seconds; `--output-bytes` sets the shared media/package
output bound. These controls are not an OS sandbox or an aggregate job deadline.

Dry-run semantics match each API: naming and album preparation can probe inputs,
and album preparation decodes artwork. They do not publish outputs. Conversion
and effect previews validate structural intent/destinations; they do not certify
that all media will decode, encoders exist, or the final output will satisfy a
provider. FFmpeg/ffprobe must be on PATH for media work.

## Configuration files

Configuration is a UTF-8 JSON object, optionally with a BOM, read from a regular
file with a 1 MiB limit. Duplicate keys, non-finite constants, unknown top-level
fields, unknown effect types, and invalid canonical metadata types are rejected.
There is no dynamic import, shell command, filter expression, or executable
configuration. Keep copies of reviewed config files with your project.

All command, output, artwork, sidecar, and config file paths resolve from the
process working directory. Metadata keys and `track_order` entries resolve from
the selected audio directory. Relative paths inside config are **not** based on
the config file's location. Quote spaces and wildcard patterns for your shell.

`naming.json`:

```json
{
  "profile": {
    "directory": "{album_artist} - {album}",
    "filename": "{track_number:02} - {title}"
  },
  "metadata": {
    "first.wav": {
      "album_artist": "Example Artist", "album": "Example Album",
      "track_number": 1, "title": "First"
    }
  }
}
```

Metadata must cover every selected file when supplied. Omit `metadata` to probe
canonical tags. See [naming profiles](NAMING_PROFILES.md) for template fields,
defaults, transformations, and missing-field behavior.

For `rename` or `album`, `filename_pattern` can replace `metadata` with an explicit
basename grammar such as `"{track_number:02} - {title}"`. They are mutually
exclusive; when neither is supplied, existing tag probing applies.
See [filename parsing](FILENAME_PARSING.md)
for exact matching and delimiter rules. Parsing never writes tags or guesses fields.

`effects.json`:

```json
{"effects": [{"type": "gain", "amount_db": -3}, {"type": "pad", "pad_out": 0.25}]}
```

Supported types and fields: `gain` (`amount_db`), `fade` (`fade_in`, `fade_out`),
`pad` (`pad_in`, `pad_out`), `low_pass`/`high_pass` (`cutoff_hz`), and
`invert_phase` (`channel`: `both`, `left`, or `right`). Times are seconds.
Supply 1–64 effects in processing order. Output settings require `--format`;
supported flags include `--sample-rate`, `--bit-depth`, `--bit-rate` (kb/s),
`--channels`, `--profile`, `--allow-lossy`, and `--drop-artwork`. See
[audio chains](AUDIO_CHAINS.md) and [conversion](FFMPEG_CONVERSION.md) for limits.

`album.json`:

```json
{
  "release": {"title": "Example Album", "artist": "Example Artist"},
  "artwork": "art/cover.jpg",
  "metadata": {
    "first.wav": {"title": "First", "disc_number": 1, "track_number": 1}
  },
  "sidecars": {"notes.txt": "notes.txt"}
}
```

Additional album fields: `track_order`, `default_disc`, `audio_format`,
`allow_audio_changes`, `allow_lossy`, and `naming` (a naming-profile object).
The service is selected with `--service`; generic is the default. See
[album packaging](ALBUM_PACKAGING.md) for the eight provider subsets, standalone
artwork requirements, checksums, and manual submission review. Release metadata,
source names/tags, and sidecars may contain personal information; inspect output
before sharing it.

## Remaining interface work

This CLI has no interactive menus, saved job
replay, or arbitrary multi-operation configuration. Opt-in v1 JSON contracts and
initial portable fixtures are available; broader cross-language conformance and
finer media-time progress remain part of readiness work. Optional
`[cli]` dependencies remain available for compatibility but are not imported.
The implementation uses Python 3.10-compatible
[argparse](https://docs.python.org/3.10/library/argparse.html) and
[signal handling](https://docs.python.org/3.10/library/signal.html).
