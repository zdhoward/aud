# Album packaging (unreleased)

`Dir.plan_album()` prepares a local ZIP; `Dir.preview()` validates and describes
it, and `Dir.execute()` writes it. `Dir.package_album()` combines preparation
and execution and returns a `BatchResult`. Sources and the selection stay intact.
FFmpeg and ffprobe must be available, including for generic input inspection.

```python
from aud import AudioMetadata, Dir

d = Dir("masters", extensions=["wav"])
plan = d.plan_album(
    "delivery/amuse.zip",
    service="amuse",
    release={"title": "Example Album", "artist": "Example Artist"},
    metadata={
        "first.wav": AudioMetadata(title="First", disc_number=1, track_number=1),
        "second.wav": AudioMetadata(title="Second", disc_number=1, track_number=2),
    },
    artwork="art/cover.jpg",
    sidecars={"notes.txt": "notes.txt"},
)
print(d.preview(plan).to_dict())
result = d.execute(plan, cancel=lambda: False)
print(result.to_dict())
```

Metadata and `track_order` keys are relative to the selected `Dir`; target,
artwork, and sidecar source paths are relative to the process working directory.
Supplied metadata must cover every selected track. Otherwise preparation probes
canonical metadata from the files. Resolve reported parsing issues first.
Release title and artist are required; additional JSON fields are retained.

## Generic packages

The default `service="generic"` copies audio byte for byte, preserves selection
order, and accepts optional artwork and explicitly named sidecars. A `naming=`
[`NamingProfile`](NAMING_PROFILES.md) can name archive members. Audio, artwork,
and sidecar names must share a collision-free portable namespace. Generic
packaging never changes audio properties or embedded tags.

Cue sheets, logs, and other sidecars are opaque files. Their references are not
followed, rewritten, or validated. If naming changes audio filenames, supply
matching sidecars yourself. No extraction log, provenance record, identifier,
or quality claim is fabricated.

## Delivery packages

These profiles prepare files for extraction and manual upload to a distributor.
The ZIP and manifest are aud formats, not distributor bulk-import formats.
There is no account connection, automatic submission, or acceptance certificate.

Service packages use `audio/0001.wav` (or FLAC), `cover.jpg`, optional `extras/`,
`manifest.json`, and `checksums.sha256`. Restricted ASCII filename stems avoid
common portal filename restrictions. A custom naming profile must produce a
single compatible filename per track.

Track order comes from explicit disc/track positions. Use `default_disc=1` only
when that is correct for the release, or supply a complete `track_order` list.
Each track needs a title. Credits, identifiers, explicit flags, genre, dates,
artist identities, and release-type rules still need review in the upload form.

Accepted source rate/depth are preserved. Unsupported properties use 44.1 kHz,
16-bit stereo only with `allow_audio_changes=True`. Bit-depth reduction to 16
bits uses triangular dither. Recognized lossy inputs require `allow_lossy=True`
and receive `lossy_source_derivative`. Unknown or ambiguous codecs, including
WavPack's possible hybrid mode, also require this opt-in and receive
`unverified_source_derivative`. The known-lossless codec allowlist excludes
companded PCM (A-law, mu-law, VIDC); a `pcm_` name alone is not enough.
Converting to WAV/FLAC does not restore lost detail.
An unknown source depth is represented as unknown, with a planned 16-bit output.
The tool cannot certify the source's earlier encoding history.

Service audio deliberately strips embedded tags and artwork: portal metadata
and standalone artwork are authoritative. Ordinary conversion behavior retains
its existing preservation defaults.

All service profiles use a conservative shared artwork subset: an existing
3000 x 3000 baseline/progressive, 8-bit, three-component JPEG smaller than
10,000,000 bytes, decoded before writing. This does not establish RGB ICC
correctness, DPI, rights, text compliance, or visual quality. No resizing or
upscaling happens automatically. Review those details against the linked guides.

## Versioned delivery profiles

Revision 1, guides checked 2026-10-14. These are supported subsets, not exhaustive
lists of everything each provider accepts. Common rates below mean 44.1, 48,
88.2, 96, 176.4, and 192 kHz, at 16 or 24 bits. Stereo is required locally.
`audio_format=` can select another listed format; the first is the default.

| Service | Local audio subset | Additional local checks / source guides |
| --- | --- | --- |
| Amuse | WAV, FLAC; common rates/depths | [Upload](https://support.amuse.io/en/articles/107727-how-to-upload-music-to-amuse-step-by-step-guide), [artwork](https://support.amuse.io/en/articles/107739-what-is-important-when-it-comes-to-artwork) |
| DistroKid | WAV, FLAC; common rates/depths | Files <1 GB; tracks <5 hours; release <=10 hours; average track >=60 seconds. [Audio](https://support.distrokid.com/hc/en-us/articles/360013647753-What-Audio-File-Formats-Can-I-Upload), [artwork](https://support.distrokid.com/hc/en-us/articles/360013534334-What-Are-the-Requirements-for-Album-Artwork) |
| TuneCore | WAV; 44.1 kHz/16-bit or 192 kHz/24-bit | Narrow verified alternatives; no automatic upsampling. [Audio](https://support.tunecore.com/hc/en-au/articles/115006499327-Uploading-Audio-Files), [artwork](https://support.tunecore.com/hc/en-in/articles/115006685728-What-are-TuneCore-s-cover-art-formatting-guidelines) |
| CD Baby | WAV, FLAC; 44.1 kHz/16-bit | [Audio](https://support.cdbaby.com/hc/en-us/articles/204498645-How-do-I-upload-my-audio), [artwork](https://support.cdbaby.com/hc/en-us/articles/360037660592-Artwork-Requirements) |
| RouteNote | FLAC; 44.1 kHz/16-bit | Standard delivery only; separate HiRes offering is outside this profile. [Audio](https://support.routenote.com/kb-article/what-are-the-audio-file-requirements/), [artwork](https://support.routenote.com/kb-article/what-are-the-album-artwork-requirements/) |
| Ditto | WAV; common rates/depths | [Audio](https://support.dittomusic.com/en/articles/4283815-what-format-does-my-audio-need-to-be-in), [artwork](https://support.dittomusic.com/en/articles/4283816-what-format-does-my-artwork-need-to-be-in) |
| LANDR | WAV, FLAC; common rates/depths | <=30 tracks; track <=60 minutes; release <=120 minutes. [Requirements](https://support.landr.com/hc/en-us/articles/115009567567-What-do-I-need-before-submitting-a-release), [artwork](https://support.landr.com/hc/en-us/articles/43916788854807-Cover-Art-Requirements), [durations](https://support.landr.com/hc/en-us/articles/31618047542167-What-kinds-of-releases-can-I-distribute-with-LANDR) |
| UnitedMasters | FLAC, WAV; common rates/depths except 88.2 kHz | [Lossless audio](https://news.unitedmasters.com/blog/losslessaudio), [artwork](https://support.unitedmasters.com/hc/en-us/articles/29586138045459-How-do-I-size-my-cover-art-correctly) |

Names ignore case, spaces, and hyphens (`"CD Baby"`, `"DistroKid"`). Inspect
`DELIVERY_PROFILES` or `delivery_profile(name)` for machine-readable settings,
revision, date, and sources. Update profiles and fixtures together when guides
change. Provider acceptance and store-specific rules can change independently.

## Publication, limits, and manifest

The complete ZIP is staged beside its destination, then published using the
shared overwrite policy. Failed or cancelled work removes owned temporary files
and leaves an existing destination intact. One grouped result covers the package;
individual payload hashes are in successful result details. Preparation errors
raise; the convenience method also records them in `last_result` and supports
`continue_on_error=True`. Cancellation returns a cancelled result.

Plans recheck input identity, size, and modification time, member collisions,
metadata budgets, and profile settings before writing and before publication.
These checks catch ordinary edits, not hostile concurrent filesystem changes.
Do not edit sources or replace ancestors during execution.

The local cap is 1000 tracks (LANDR: 30), 64 sidecars, and 64 MiB per sidecar or
generic artwork. Service audio has a local <4 GB cap, reduced to <1 GB for
DistroKid. Other caps are safety choices, not claimed provider limits.
`MediaLimits.output_bytes` bounds the whole archive and each conversion;
`stdout_bytes` bounds aggregate metadata and final manifest JSON. Process limits
are polled application controls, not an OS sandbox or hard memory quotas.

Manifest schema version 1 records release/track metadata, ordered members,
source/output properties, transformations, profile revision/sources, payload
sizes and SHA-256 hashes, effective encoder/version and dither policy for
converted payloads, artwork review status, and a manual checklist.
Generated manifest paths are archive-relative; caller-supplied metadata and
sidecars can still contain personal information. Review them before sharing.
The checksum file covers payloads and manifest, excluding itself. ZIP timestamps
and encoder versions can vary, so whole-archive byte reproducibility is not promised.
