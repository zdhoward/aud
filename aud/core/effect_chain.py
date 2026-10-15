"""Compile supported effect intents into a fixed, numeric FFmpeg filter chain."""

from __future__ import annotations

import math

from aud.core.operations.audio.effects import (
    Fade,
    Gain,
    HighPassFilter,
    InvertPhase,
    LowPassFilter,
    Pad,
)

SUPPORTED = (Gain, Fade, Pad, LowPassFilter, HighPassFilter, InvertPhase)


def validate_effects(effects) -> None:
    if not effects:
        raise ValueError("AudioChain needs at least one effect")
    for effect in effects:
        if not isinstance(effect, SUPPORTED):
            raise TypeError(f"Unsupported chain effect: {type(effect).__name__}")
        if isinstance(effect, InvertPhase):
            if getattr(effect, "channel", None) not in {"both", "left", "right"}:
                raise ValueError("Phase channel must be both, left, or right")
            continue
        names = (
            ("amount_db",)
            if isinstance(effect, Gain)
            else (
                ("fade_in", "fade_out")
                if isinstance(effect, Fade)
                else ("pad_in", "pad_out") if isinstance(effect, Pad) else ("cutoff_hz",)
            )
        )
        for name in names:
            value = getattr(effect, name, None)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(f"{name} must be a finite number")
            if not isinstance(effect, Gain) and value < 0:
                raise ValueError(f"{name} must be nonnegative")
        if isinstance(effect, (LowPassFilter, HighPassFilter)) and effect.cutoff_hz <= 0:
            raise ValueError("Filter cutoff must be positive")


def compile_effects(effects, sample_rate: int, channels: int, duration: float | None):
    validate_effects(effects)
    filters = ["aformat=sample_fmts=dbl"]
    for effect in effects:
        if isinstance(effect, Gain):
            filters.append(f"volume={effect.amount_db:.17g}dB:precision=double")
        elif isinstance(effect, Pad):
            before, after = round(effect.pad_in * sample_rate), round(effect.pad_out * sample_rate)
            if before:
                filters.append(f"adelay=delays={before}S:all=1")
            if after:
                filters.append(f"apad=pad_len={after}")
            if duration is not None:
                duration += (before + after) / sample_rate
        elif isinstance(effect, Fade):
            if effect.fade_in:
                filters.append(f"afade=t=in:d={effect.fade_in:.17g}")
            if effect.fade_out:
                if duration is None or effect.fade_out > duration:
                    raise ValueError(
                        "Fade-out requires a known duration at least as long as the fade"
                    )
                filters.append(
                    f"afade=t=out:st={duration - effect.fade_out:.17g}:d={effect.fade_out:.17g}"
                )
        elif isinstance(effect, (LowPassFilter, HighPassFilter)):
            if effect.cutoff_hz >= sample_rate / 2:
                raise ValueError("Filter cutoff must be below the source Nyquist frequency")
            name = "lowpass" if isinstance(effect, LowPassFilter) else "highpass"
            filters.append(f"{name}=f={effect.cutoff_hz:.17g}:p=1:r=f64")
        elif effect.channel == "both":
            filters.append("volume=-1:precision=double")
        else:
            if channels != 2:
                raise ValueError("Left/right phase inversion requires stereo input")
            filters.append(
                "pan=stereo|c0=-1*c0|c1=c1"
                if effect.channel == "left"
                else "pan=stereo|c0=c0|c1=-1*c1"
            )
    return filters, duration
