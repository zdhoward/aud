from __future__ import annotations

import shutil

from pydub import AudioSegment
from pydub.utils import mediainfo_json

from aud.core.adapters.batch import BatchAdapter
from aud.core.models import AudioFile
from aud.core.safety import Destination, check_path, staged_write


class AudioIO(BatchAdapter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.metadata: dict = {}
        self.destination: Destination | None = None

    def _load(self, file: AudioFile) -> AudioSegment:
        for tool in ("ffmpeg", "ffprobe"):
            if shutil.which(tool) is None:
                raise RuntimeError(
                    f"{tool} is required for audio processing; install FFmpeg and add it to PATH"
                )
        check_path(file.path)
        info = mediainfo_json(str(file.path))
        self.metadata = info
        return AudioSegment.from_file(file.path, file.extension)

    def _export(self, audio: AudioSegment, file: AudioFile, format=None, **kwargs):
        format = format or file.extension
        tags = dict(self.metadata.get("format", {}).get("tags", {}))
        tags.pop("encoder", None)
        tags.update(kwargs.pop("tags", None) or {})
        if tags and format in {"mp3", "flac", "ogg"}:
            kwargs["tags"] = tags
        if format == "mp3" and "bitrate" not in kwargs:
            stream: dict = next(
                (s for s in self.metadata.get("streams", []) if s.get("codec_type") == "audio"), {}
            )
            if stream.get("codec_name") == "mp3" and stream.get("bit_rate"):
                kwargs["bitrate"] = f"{round(int(stream['bit_rate']) / 1000)}k"
        entry = self.destination or Destination(file.path, file.path, replace=True)
        with staged_write(entry) as temporary:
            exported = audio.export(temporary, format=format, **kwargs)
            exported.close()
            if format == "raw":
                if temporary.stat().st_size != len(audio.raw_data):
                    raise ValueError("Raw output byte length mismatch")
            else:
                verified = AudioSegment.from_file(temporary, format)
                if verified.channels != audio.channels or verified.frame_rate != audio.frame_rate:
                    raise ValueError("Encoded output channels/sample rate mismatch")
                if len(audio) and not len(verified):
                    raise ValueError("Encoded output is empty")
