"""Versioned, conservative local delivery presets, not portal acceptance certificates."""

from dataclasses import asdict, dataclass
from types import MappingProxyType

RATES = (44100, 48000, 88200, 96000, 176400, 192000)
HIRES = tuple((rate, bits) for rate in RATES for bits in (16, 24))


@dataclass(frozen=True)
class DeliveryProfile:
    name: str
    formats: tuple[str, ...]
    audio_pairs: tuple[tuple[int, int], ...]
    sources: tuple[str, ...]
    revision: int = 1
    checked_on: str = "2026-10-14"
    max_audio_bytes: int = 4_000_000_000
    max_tracks: int = 1000
    max_track_seconds: int | None = None
    max_release_seconds: int | None = None
    min_average_seconds: int = 0
    track_limit_exclusive: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


_PROFILES = [
    DeliveryProfile("generic", (), (), ()),
    DeliveryProfile(
        "amuse",
        ("wav", "flac"),
        HIRES,
        (
            "https://support.amuse.io/en/articles/107727-how-to-upload-music-to-amuse-step-by-step-guide",
            "https://support.amuse.io/en/articles/107739-what-is-important-when-it-comes-to-artwork",
        ),
    ),
    DeliveryProfile(
        "distrokid",
        ("wav", "flac"),
        HIRES,
        (
            "https://support.distrokid.com/hc/en-us/articles/360013647753-What-Audio-File-Formats-Can-I-Upload",
            "https://support.distrokid.com/hc/en-us/articles/360013534334-What-Are-the-Requirements-for-Album-Artwork",
        ),
        max_audio_bytes=1_000_000_000,
        max_track_seconds=18000,
        max_release_seconds=36000,
        min_average_seconds=60,
        track_limit_exclusive=True,
    ),
    DeliveryProfile(
        "tunecore",
        ("wav",),
        ((44100, 16), (192000, 24)),
        (
            "https://support.tunecore.com/hc/en-au/articles/115006499327-Uploading-Audio-Files",
            "https://support.tunecore.com/hc/en-in/articles/115006685728-What-are-TuneCore-s-cover-art-formatting-guidelines",
        ),
    ),
    DeliveryProfile(
        "cdbaby",
        ("wav", "flac"),
        ((44100, 16),),
        (
            "https://support.cdbaby.com/hc/en-us/articles/204498645-How-do-I-upload-my-audio",
            "https://support.cdbaby.com/hc/en-us/articles/360037660592-Artwork-Requirements",
        ),
    ),
    DeliveryProfile(
        "routenote",
        ("flac",),
        ((44100, 16),),
        (
            "https://support.routenote.com/kb-article/what-are-the-audio-file-requirements/",
            "https://support.routenote.com/kb-article/what-are-the-album-artwork-requirements/",
        ),
    ),
    DeliveryProfile(
        "ditto",
        ("wav",),
        HIRES,
        (
            "https://support.dittomusic.com/en/articles/4283815-what-format-does-my-audio-need-to-be-in",
            "https://support.dittomusic.com/en/articles/4283816-what-format-does-my-artwork-need-to-be-in",
        ),
    ),
    DeliveryProfile(
        "landr",
        ("wav", "flac"),
        HIRES,
        (
            "https://support.landr.com/hc/en-us/articles/115009567567-What-do-I-need-before-submitting-a-release",
            "https://support.landr.com/hc/en-us/articles/43916788854807-Cover-Art-Requirements",
            "https://support.landr.com/hc/en-us/articles/31618047542167-What-kinds-of-releases-can-I-distribute-with-LANDR",
        ),
        max_tracks=30,
        max_track_seconds=3600,
        max_release_seconds=7200,
    ),
    DeliveryProfile(
        "unitedmasters",
        ("flac", "wav"),
        tuple(pair for pair in HIRES if pair[0] != 88200),
        (
            "https://news.unitedmasters.com/blog/losslessaudio",
            "https://support.unitedmasters.com/hc/en-us/articles/29586138045459-How-do-I-size-my-cover-art-correctly",
        ),
    ),
]
DELIVERY_PROFILES = MappingProxyType({profile.name: profile for profile in _PROFILES})


def delivery_profile(name: str) -> DeliveryProfile:
    try:
        return DELIVERY_PROFILES[name.casefold().replace("-", "").replace(" ", "")]
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError(f"Unknown delivery profile: {name}") from error
