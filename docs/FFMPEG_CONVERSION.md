# FFmpeg conversion contract

The conversion adapter uses FFmpeg directly; effects remain on the existing pydub
backend during this migration. This slice does not claim Python 3.13+ support for
the complete package. Existing conversion methods and boolean helpers stay available.

Conversion probes a regular local input, writes to an owned staging file, probes
and decodes the output, and publishes only after verification. Output rate/channels
and PCM depth must match the effective request. Lossless-input WAV/FLAC conversions
also check duration within rounding/resampling tolerance. WAV/raw support 8/16/24/32-bit PCM;
the supported FLAC encoding path is 16/24-bit. Conversion does not load decoded
tracks into Python memory. Raw PCM uses explicit format properties for validation.

Ordinary primary-audio and container tags are carried forward. Container values
win over matching audio-stream values; explicit tags override both.
Attached JPEG/PNG artwork is copied for MP3/FLAC. Formats unable to carry artwork
reject it unless `drop_artwork=True` is explicit. Unsupported metadata is reported
instead of being presented as preserved. Encoder-generated tags are not inherited.

Optional neutral profiles are `flac-preserve`, `mp3-v0`, `mp3-v2`, and `mp3-320`.
Profiles require a visibly lossless source codec unless `allow_lossy=True` is
explicit; this is a codec check, not certification of original source provenance.
The preservation profile rejects requested sample-property changes. Generic
conversion retains its compatibility behavior and permits deliberate lossy inputs.
VBR quality is explicit and is never inferred from average source bitrate.

`MediaLimits` configures per-process timeout, diagnostic/probe output limits, and
encoded output size. Tools receive argument arrays, no shell or inherited stdin,
an allowlisted environment, local protocols/demuxers, and one codec worker thread.
The runner polls output size and cancellation, kills and reaps its owned process
on timeout/cancellation/failure, and closes diagnostics before staging cleanup.
Completion rechecks limits and cancellation before accepting process output;
conversion checks cancellation again immediately before publication.
These application limits are not OS-enforced memory/disk quotas or an OS sandbox;
a brief output-size overshoot between polling intervals is possible. POSIX process
groups are stopped together; Windows stops the owned FFmpeg/ffprobe process.

Active cancellation is supported for conversions. pydub effects still stop only
between files. Callers must use a patched FFmpeg build and avoid concurrently
editing sources or replacing their ancestors. Decoder security and external-tool
patching remain independent requirements.

Targeted acceptance checks cover 24-bit PCM round trips, tags/artwork, profile
settings, invalid parameters, timeout/cancellation cleanup, staged failure, and
the conversion/export callers. Full-suite and coverage checks are reserved for
release validation.

References: [FFmpeg codecs](https://ffmpeg.org/ffmpeg-codecs.html),
[FFmpeg command options](https://ffmpeg.org/ffmpeg.html),
[protocol controls](https://ffmpeg.org/ffmpeg-protocols.html), and
[Python subprocess management](https://docs.python.org/3/library/subprocess.html).
