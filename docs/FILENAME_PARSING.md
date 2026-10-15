# Explicit filename parsing (unreleased)

`FilenamePattern` extracts canonical metadata from a caller-chosen basename
grammar. It does not guess a convention, inspect parent directories, probe audio,
merge existing tags, or write tags/files. Treat parsed values as candidates to
review before using them for naming or delivery.

```python
from aud import Dir, FilenamePattern, NamingProfile

pattern = FilenamePattern("{disc_number:02}-{track_number:02} - {title}")
metadata = pattern.parse("02-03 - Café.flac")
assert metadata.disc_number == 2
assert metadata.track_number == 3
assert metadata.title == "Café"

d = Dir("masters", extensions=["flac"])
rows = d.parse_filenames(pattern)
plan = d.plan_naming(
    NamingProfile(directory="Disc {disc_number:02}", filename="{track_number:02} - {title}"),
    "organized", metadata=rows, copy=True,
)
print(d.preview(plan).to_dict())
result = d.execute(plan)
```

`parse()` takes a string or `Path` containing one basename with an explicit
alphanumeric extension (1–16 ASCII characters). Only the last suffix is removed:
`Part.One.wav` has stem `Part.One`. Extension case does not affect extraction.
`Dir.parse_filenames()` parses the current selection and returns an absolute-path
metadata mapping suitable for `plan_naming()` or `plan_album()`. Any mismatch
raises; it returns no partial mapping and changes no files or selection.

## Grammar and matching rules

Fields are `artist`, `album_artist`, `album`, `title`, `year`, `track_number`,
`track_total`, `disc_number`, and `disc_total`. Each field can appear once.
Fields must be separated by literal text. Prefixes/suffixes are literal too;
use `{{` and `}}` for literal braces. Attribute/index access, conversions,
arbitrary format expressions, and regular expressions are unsupported.

Numeric fields accept positive ASCII decimal integers with at most nine digits.
Optional widths `1`–`9` or `01`–`09` require exactly that many input digits;
`{track_number:02}` accepts `03` and rejects `3`. Zero and values where a supplied
track/disc number exceeds its supplied total fail. Year is a numeric field, not
a calendar-date or release-history assertion.

Matching proceeds left to right using the first occurrence of each next literal
separator, without backtracking or heuristic confidence scores. With
`{artist} - {title}`, `A - B - C.wav` means artist `A`, title `B - C`.
If `A - B` is the intended artist, that pattern is unsuitable: choose a different
delimiter or supply metadata explicitly. The parser does not claim this split
is the only possible interpretation. It consumes the complete stem; extra text
after a required literal suffix fails.

Text captures preserve Unicode, case, and leading/trailing whitespace exactly;
empty or whitespace-only captures fail. Naming-profile transformations remain
a separate explicit step. Parsed metadata has empty original tags and issues,
because none were read. There is no implicit precedence between filenames and
tags; use deliberate application code if merging is needed.

Templates are bounded to 2048 characters, filenames to 4096. Path separators and
control/format/surrogate characters are rejected. These are parsing limits, not
a portable-filesystem validator or security sandbox. Naming/output preflight
still enforces its own component and collision rules.

## CLI configuration

For `rename` and `album`, use a `filename_pattern` string instead of `metadata`:

```json
{
  "filename_pattern": "{track_number:02} - {title}",
  "profile": {"directory": "", "filename": "{title}"}
}
```

```shell
aud rename masters --extensions flac --config naming.json --output-directory organized --copy --dry-run
```

Album config uses the same field alongside its explicit release metadata:

```json
{
  "release": {"title": "Example Album", "artist": "Example Artist"},
  "filename_pattern": "{track_number:02} - {title}",
  "default_disc": 1,
  "artwork": "art/cover.jpg"
}
```

Choose `default_disc` deliberately for single-disc service delivery. All selected
files must match. Supplying both `metadata` and `filename_pattern` is rejected,
including an empty metadata object. Without either field, existing probing
behavior stays unchanged. See [CLI](CLI.md), [naming](NAMING_PROFILES.md), and
[album packaging](ALBUM_PACKAGING.md) for the other requirements.

Portable valid/mismatch examples live in
[`conformance/v1/filename.json`](../conformance/v1/filename.json).
