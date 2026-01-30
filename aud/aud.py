from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from aud.core.adapters.audio import AudioAdapter
from aud.core.adapters.convert import ConversionAdapter
from aud.core.adapters.filesystem import FileSystemAdapter
from aud.core.models import AudioFile
from aud.core.operations.archive import Zip

# conversion
from aud.core.operations.audio.convert import (
    ConvertFormat,
    ConvertToMono,
    ConvertToStereo,
)

# audio operations
from aud.core.operations.audio.effects import (
    AppendAudio,
    AudioJoin,
    Fade,
    Gain,
    HighPassFilter,
    InvertPhase,
    LowPassFilter,
    Normalize,
    Pad,
    PrependAudio,
    StripSilence,
    Watermark,
)

# file operations
from aud.core.operations.files import Backup, Copy, Move

# filename operations
from aud.core.operations.names import (
    Append,
    Iterate,
    Lowercase,
    Prepend,
    Replace,
    ReplaceSpaces,
    Uppercase,
)
from aud.core.plan import Plan
from aud.core.selection.composite import CompositePolicy

# selection
from aud.core.selection.extensions import ExtensionPolicy
from aud.core.selection.listing import AllowlistPolicy, DenylistPolicy
from aud.core.selection.policy import SelectionPolicy
from aud.core.selection.scanner import DirectoryScanner

# exceptions (kept)
from aud.exceptions import (
    AudioFXError,
    ConvertError,
    ExportError,
    FileError,
    FilenameError,
)


class _AlwaysFalsePolicy(SelectionPolicy):
    def include(self, file: AudioFile) -> bool:
        return False


@dataclass(frozen=True)
class _AllowlistOverridesPolicy(SelectionPolicy):
    """
    Matches legacy v1 behavior:

        (valid_extension AND not_denylisted) OR allowlisted

    Also matches legacy detail:
    - If extensions is empty: valid_extension is always False, so only allowlist can include.
    """

    allow: AllowlistPolicy
    base: SelectionPolicy

    def include(self, file: AudioFile) -> bool:
        if self.allow.include(file):
            return True
        return self.base.include(file)


class Dir:
    """
    Public façade for aud.

    Dir is intentionally thin:
    - builds selection policies
    - builds plans
    - dispatches to adapters
    """

    def __init__(
        self,
        directory: str | Path = ".",
        extensions: Iterable[str] | None = None,
        allowlist: Iterable[str] | None = None,
        denylist: Iterable[str] | None = None,
    ):
        self.directory = Path(directory).resolve()

        self._extensions = list(extensions or [])
        self._allowlist = list(allowlist or [])
        self._denylist = list(denylist or [])

        # optional regex-based selection (supported by your policy classes)
        self._allowlist_regex: str | None = None
        self._denylist_regex: str | None = None

        # kept for config parity (not used by core right now)
        self._logfile: Path | None = None

        self._files: list[AudioFile] = []
        self.update()

    # ------------------------------------------------------------------
    # basic protocol
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._files)

    def __iter__(self) -> Iterator[AudioFile]:
        return iter(self._files)

    def get_all(self) -> list[str]:
        return [f.path.name for f in self._files]

    def get_single(self, num: int) -> str:
        return self._files[num].path.name

    def log(self, message: str) -> bool:
        import datetime

        if not self._logfile:
            return False
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")
            with open(self._logfile, "a") as file:
                file.write(f"{timestamp}: {message}\n")
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # selection (LEGACY-PARITY)
    # ------------------------------------------------------------------

    def _build_policy(self) -> SelectionPolicy:
        # Base policy = valid extension AND not denylisted.
        # Important legacy parity:
        # - If extensions is empty, NOTHING matches unless allowlisted.
        base_policies: list[SelectionPolicy] = []

        if self._extensions:
            base_policies.append(ExtensionPolicy(self._extensions))
        else:
            base_policies.append(_AlwaysFalsePolicy())

        if self._denylist or self._denylist_regex:
            base_policies.append(DenylistPolicy(self._denylist, regex=self._denylist_regex))

        base = CompositePolicy(*base_policies)

        # Allowlist overrides base if present (names or regex).
        if self._allowlist or self._allowlist_regex:
            allow = AllowlistPolicy(self._allowlist, regex=self._allowlist_regex)
            return _AllowlistOverridesPolicy(allow=allow, base=base)

        return base

    def update(self) -> None:
        scanner = DirectoryScanner(self.directory, self._build_policy())
        self._files = scanner.scan()

    # ------------------------------------------------------------------
    # config (compat layer)
    # ------------------------------------------------------------------

    def config_set_extensions(self, extensions: Iterable[str]) -> bool:
        self._extensions = list(extensions or [])
        self.update()
        return True

    def config_get_extensions(self) -> list[str]:
        return list(self._extensions)

    def config_set_allowlist(
        self, names: Iterable[str] | None = None, regex: str | None = None
    ) -> bool:
        self._allowlist = list(names or [])
        self._allowlist_regex = regex
        self.update()
        return True

    def config_set_denylist(
        self, names: Iterable[str] | None = None, regex: str | None = None
    ) -> bool:
        self._denylist = list(names or [])
        self._denylist_regex = regex
        self.update()
        return True

    def config_set_log_file(self, filename: str = "main.log") -> bool:
        self._logfile = Path(filename).resolve()
        return True

    def config_get_allowlist(self) -> list[str]:
        return list(self._allowlist)

    def config_get_denylist(self) -> list[str]:
        return list(self._denylist)

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _execute_filesystem(self, plan: Plan) -> None:
        adapter = FileSystemAdapter()
        files = plan.files

        for op in plan.operations:
            files = adapter.execute(op, files)

        self._files = files

    def _execute_audio(self, plan: Plan) -> None:
        adapter = AudioAdapter()
        files = plan.files

        for op in plan.operations:
            files = adapter.execute(op, files)

        self._files = files

    def _execute_convert(self, plan: Plan) -> None:
        adapter = ConversionAdapter()
        files = plan.files

        for op in plan.operations:
            files = adapter.execute(op, files)

        self._files = files

    def _plan(self) -> Plan:
        return Plan(list(self._files))

    # ------------------------------------------------------------------
    # name operations
    # ------------------------------------------------------------------

    def name_upper(self) -> bool:
        try:
            plan = self._plan().add(Uppercase())
            self._execute_filesystem(plan)
            return True
        except Exception as e:
            raise FilenameError("uppercase", e)

    def name_lower(self) -> bool:
        try:
            plan = self._plan().add(Lowercase())
            self._execute_filesystem(plan)
            return True
        except Exception as e:
            raise FilenameError("lowercase", e)

    def name_append(self, suffix: str) -> bool:
        try:
            plan = self._plan().add(Append(suffix))
            self._execute_filesystem(plan)
            return True
        except Exception as e:
            raise FilenameError("append", e)

    def name_prepend(self, prefix: str) -> bool:
        try:
            plan = self._plan().add(Prepend(prefix))
            self._execute_filesystem(plan)
            return True
        except Exception as e:
            raise FilenameError("prepend", e)

    def name_replace(self, target: str, replacement: str) -> bool:
        try:
            plan = self._plan().add(Replace(target, replacement))
            self._execute_filesystem(plan)
            return True
        except Exception as e:
            raise FilenameError("replace", e)

    def name_replace_spaces(self, replacement: str = "_") -> bool:
        try:
            plan = self._plan().add(ReplaceSpaces(replacement))
            self._execute_filesystem(plan)
            return True
        except Exception as e:
            raise FilenameError("replace spaces", e)

    def name_iterate(self, zerofill: int = 0, separator: str = "_") -> bool:
        try:
            plan = self._plan().add(Iterate(zerofill=zerofill, separator=separator))
            self._execute_filesystem(plan)
            return True
        except Exception as e:
            raise FilenameError("iterate", e)

    # ------------------------------------------------------------------
    # file operations
    # ------------------------------------------------------------------

    def copy(self, target_directory: str | Path) -> bool:
        try:
            plan = self._plan().add(Copy(Path(target_directory)))
            self._execute_filesystem(plan)
            return True
        except Exception as e:
            raise FileError("copy", e)

    def move(self, target_directory: str | Path) -> bool:
        try:
            plan = self._plan().add(Move(Path(target_directory)))
            self._execute_filesystem(plan)
            return True
        except Exception as e:
            raise FileError("move", e)

    def backup(self, target_directory: str | Path) -> bool:
        try:
            plan = self._plan().add(Backup(Path(target_directory)))
            self._execute_filesystem(plan)
            return True
        except Exception as e:
            raise FileError("backup", e)

    def archive_zip(self, target_zip: str | Path) -> bool:
        try:
            plan = self._plan().add(Zip(Path(target_zip)))
            self._execute_filesystem(plan)
            return True
        except Exception as e:
            raise FileError("zip", e)

    def zip(self, target_zip: str | Path) -> bool:
        """Alias for archive_zip() for backward compatibility."""
        return self.archive_zip(target_zip)

    # ------------------------------------------------------------------
    # audio FX operations
    # ------------------------------------------------------------------

    def afx_normalize(self, target_level: float = 0.1, passes: int = 1) -> bool:
        try:
            plan = self._plan().add(Normalize(target_db=target_level, passes=passes))
            self._execute_audio(plan)
            return True
        except Exception as e:
            raise AudioFXError("normalize", e)

    def afx_fade(self, in_fade: float = 0, out_fade: float = 0) -> bool:
        try:
            plan = self._plan().add(Fade(fade_in=in_fade, fade_out=out_fade))
            self._execute_audio(plan)
            return True
        except Exception as e:
            raise AudioFXError("fade", e)

    def afx_pad(self, in_pad: float = 0, out_pad: float = 0) -> bool:
        try:
            plan = self._plan().add(Pad(pad_in=in_pad, pad_out=out_pad))
            self._execute_audio(plan)
            return True
        except Exception as e:
            raise AudioFXError("pad", e)

    def afx_gain(self, amount_db: float) -> bool:
        try:
            plan = self._plan().add(Gain(amount_db=amount_db))
            self._execute_audio(plan)
            return True
        except Exception as e:
            raise AudioFXError("gain", e)

    def afx_low_pass(self, cutoff_hz: int) -> bool:
        try:
            plan = self._plan().add(LowPassFilter(cutoff_hz=cutoff_hz))
            self._execute_audio(plan)
            return True
        except Exception as e:
            raise AudioFXError("low pass", e)

    def afx_high_pass(self, cutoff_hz: int) -> bool:
        try:
            plan = self._plan().add(HighPassFilter(cutoff_hz=cutoff_hz))
            self._execute_audio(plan)
            return True
        except Exception as e:
            raise AudioFXError("high pass", e)

    def afx_invert_phase(self, channel: str = "both") -> bool:
        try:
            plan = self._plan().add(InvertPhase(channel=channel))
            self._execute_audio(plan)
            return True
        except Exception as e:
            raise AudioFXError("invert phase", e)

    def afx_invert_stereo_phase(self, channel: str = "both") -> bool:
        """Alias for afx_invert_phase() for backward compatibility."""
        return self.afx_invert_phase(channel)

    def afx_lpf(self, cutoff: int) -> bool:
        """Alias for afx_low_pass() for backward compatibility."""
        return self.afx_low_pass(cutoff)

    def afx_hpf(self, cutoff: int) -> bool:
        """Alias for afx_high_pass() for backward compatibility."""
        return self.afx_high_pass(cutoff)

    def afx_strip_silence(
        self, silence_length: int = 1000, silence_threshold: int = -16, padding: int = 100
    ) -> bool:
        try:
            plan = self._plan().add(
                StripSilence(
                    silence_length=silence_length,
                    silence_threshold=silence_threshold,
                    padding=padding,
                )
            )
            self._execute_audio(plan)
            return True
        except Exception as e:
            raise AudioFXError("strip silence", e)

    def afx_watermark(
        self, watermark_file: str | Path, frequency_min: float, frequency_max: float
    ) -> bool:
        try:
            plan = self._plan().add(
                Watermark(
                    watermark_file=watermark_file,
                    frequency_min=frequency_min,
                    frequency_max=frequency_max,
                )
            )
            self._execute_audio(plan)
            return True
        except Exception as e:
            raise AudioFXError("watermark", e)

    def afx_join(self, target_location: str | Path, format: str = "wav") -> bool:
        try:
            plan = self._plan().add(AudioJoin(target_location=target_location, file_format=format))
            self._execute_audio(plan)
            return True
        except Exception as e:
            raise AudioFXError("join", e)

    def afx_prepend(self, file: str | Path) -> bool:
        try:
            plan = self._plan().add(PrependAudio(audio_file=file))
            self._execute_audio(plan)
            return True
        except Exception as e:
            raise AudioFXError("prepend audio", e)

    def afx_append(self, file: str | Path) -> bool:
        try:
            plan = self._plan().add(AppendAudio(audio_file=file))
            self._execute_audio(plan)
            return True
        except Exception as e:
            raise AudioFXError("append audio", e)

    # ------------------------------------------------------------------
    # conversion operations
    # ------------------------------------------------------------------

    def convert_format(
        self,
        target_format: str,
        sample_rate: int | None = None,
        bit_depth: int | None = None,
        tags: dict[str, str] | None = None,
        cover: str | None = None,
    ) -> bool:
        try:
            plan = self._plan().add(
                ConvertFormat(
                    target_format=target_format,
                    sample_rate=sample_rate,
                    bit_depth=bit_depth,
                    tags=tags,
                    cover=cover,
                )
            )
            self._execute_convert(plan)
            return True
        except Exception as e:
            raise ConvertError("format", e)

    def convert_mono(self) -> bool:
        try:
            plan = self._plan().add(ConvertToMono())
            self._execute_convert(plan)
            return True
        except Exception as e:
            raise ConvertError("mono", e)

    def convert_stereo(self) -> bool:
        try:
            plan = self._plan().add(ConvertToStereo())
            self._execute_convert(plan)
            return True
        except Exception as e:
            raise ConvertError("stereo", e)

    def convert_to_wav(
        self, sample_rate: int | None = None, bit_depth: int | None = None, cover: str | None = None
    ) -> bool:
        """Convenience method for converting to WAV format."""
        return self.convert_format("wav", sample_rate=sample_rate, bit_depth=bit_depth, cover=cover)

    def convert_to_mp3(
        self,
        bit_rate: int | None = None,
        bit_depth: int | None = None,
        cover: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> bool:
        """Convenience method for converting to MP3 format."""
        # Note: bit_rate parameter is kept for compatibility but pydub uses sample_rate
        return self.convert_format(
            "mp3", sample_rate=bit_rate, bit_depth=bit_depth, tags=tags, cover=cover
        )

    def convert_to_flac(
        self,
        sample_rate: int | None = None,
        bit_depth: int | None = None,
        cover: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> bool:
        """Convenience method for converting to FLAC format."""
        return self.convert_format(
            "flac", sample_rate=sample_rate, bit_depth=bit_depth, tags=tags, cover=cover
        )

    def convert_to_raw(
        self, sample_rate: int | None = None, bit_depth: int | None = None, cover: str | None = None
    ) -> bool:
        """Convenience method for converting to RAW format."""
        return self.convert_format("raw", sample_rate=sample_rate, bit_depth=bit_depth, cover=cover)

    def convert_to(
        self,
        format: str = "wav",
        sample_rate: int | None = None,
        bit_depth: int | None = None,
        cover: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> bool:
        """Alias for convert_format() for backward compatibility."""
        return self.convert_format(
            format, sample_rate=sample_rate, bit_depth=bit_depth, tags=tags, cover=cover
        )

    # ------------------------------------------------------------------
    # export helper (legacy API shape)
    # ------------------------------------------------------------------

    def export_for(self, target_platform: str, target_directory: str | Path = "export") -> bool:
        """
        Legacy-compatible entrypoint.

        NOTE: This is still a lightweight wrapper and assumes your CLI
        is deciding formats per platform elsewhere (or you’ll add that here).
        """
        try:
            # placeholder: keep the method for API parity; real mapping can live in CLI later
            platform = target_platform.strip().lower()
            out_dir = Path(target_directory)

            if platform == "amuse":
                self.copy(out_dir)
                self.convert_format("wav", sample_rate=44100, bit_depth=16)
                return True

            if platform == "cd":
                self.copy(out_dir)
                self.convert_format("wav", sample_rate=44100, bit_depth=16)
                return True

            if platform in {"wav"}:
                self.copy(out_dir)
                self.convert_format("wav")
                return True

            if platform in {"mp3"}:
                self.copy(out_dir)
                self.convert_format("mp3")
                return True

            raise ValueError(f"Unsupported platform: {target_platform}")
        except Exception as e:
            raise ExportError("export_for", e)


# Additional backward compatibility note:
# export_for() now supports "amuse" and "cd" platforms as per v1 behavior
# Both export to WAV 44.1kHz 16-bit
