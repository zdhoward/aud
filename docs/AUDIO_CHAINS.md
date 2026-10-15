# Audio chains and canonical metadata

`AudioChain` is an explicit batch operation for `Gain`, `Fade`, `Pad`,
`LowPassFilter`, `HighPassFilter`, and `InvertPhase`. It applies effects in the
given order and optionally performs a final `ConvertFormat`. Each selected file
has one processing decode and one final encode, followed by the existing output
probe/full-decode verification. Intermediate effect outputs are not published.
Existing individual effect methods retain their pydub behavior.

```python
from threading import Event

from aud import AudioChain, Dir
from aud.core.operations.audio.convert import ConvertFormat
from aud.core.operations.audio.effects import Fade, Gain, Pad

d = Dir("masters", extensions=["wav", "flac"])
event = Event()
chain = AudioChain(
    [Gain(-3), Pad(0.1, 0.2), Fade(fade_out=0.5)],
    output=ConvertFormat("mp3", profile="mp3-v0", output_directory="listening"),
)
plan = d.plan().add(chain)
print(d.preview(plan).to_dict())
result = d.execute(plan, continue_on_error=True, cancel=event.is_set)
```

The example's `event` is a caller-owned cancellation signal. Omit `cancel` if no
cancellation signal is needed. For boolean convenience use
`d.afx_chain(effects, output=conversion)`. Without `output`, the chain publishes
in place with the source format and sample properties. For lossy sources this
still creates a new lossy generation; it does not preserve VBR preset identity.
Conversion profiles retain their existing lossless-input opt-in rule.

The native chain starts with double-precision samples and quantizes only at the
final encoding boundary. Gain can exceed full scale during processing; the final
integer/lossy encoding can clip. Low/high-pass filters use FFmpeg's one-pole
implementation. Native output is not promised to match pydub's sample rounding
or filter response. Padding rounds seconds to the nearest source sample (ties to
even), and fade-out is measured from the current duration after preceding pads.
A fade-out longer than the known track duration is rejected.
For fade-out on lossy input or unavailable header duration, a bounded analysis
decode measures actual duration first, avoiding encoder-padding timing errors.
This analysis adds a decode pass; it does not create an intermediate encode.
Left/right phase inversion requires stereo; `both` applies to all channels. Filter cutoffs must be
positive and below source Nyquist. No user-supplied filter strings are accepted.

Pure parameter validation runs during construction and plan preflight. Duration,
channel, and cutoff checks require a per-file probe and run before that file's
encode. A chain is atomic per file through staged publication; batches retain
earlier successful outputs on later failure. Results identify one `AudioChain`
outcome per file and list its ordered effects in `details`. Existing dependency,
selection, artwork, metadata-loss reporting, process limits, and cancellation
behavior applies. The filesystem and resource limits are documented in the
[conversion contract](FFMPEG_CONVERSION.md).

Peak normalization, silence removal, joins, sidecar insertion, and random
watermarks remain on the legacy backend and are rejected inside `AudioChain`.
Repeated separate `Dir` calls still encode separately; use an explicit chain to
avoid intermediate encodes. This partial migration does not remove pydub or
enable whole-package Python 3.13+ support.

`AudioMetadata.from_tags(tags)` provides artist, album artist, album, title,
year, track/disc numbers and totals, the original tag mapping, and parsing issues.
It accepts common FFmpeg ID3/Vorbis names, including `track`/`tracknumber`,
`disc`/`discnumber`, fraction positions such as `03/12`, and explicit totals.
Year/date supports a four-digit year or ISO year-month/day; matching date/year
values agree by year. Position numbers are positive ASCII integers of at most
nine digits. Conflicting aliases/totals and invalid values produce issues and
nullable canonical fields, rather than fabricated values or tag changes.
Missing fields remain null. Unknown tags stay in `tags`.

Conversion and chain results include `source_metadata` and `output_metadata`;
raw PCM has null output metadata. The view does not write tags, infer fields from
filenames, or certify provenance. Future naming profiles must explicitly handle
missing fields and parsing issues before generating destinations.

References: [FFmpeg audio filters](https://ffmpeg.org/ffmpeg-filters.html),
[FFmpeg metadata mapping](https://ffmpeg.org/ffmpeg.html#Advanced-options).
