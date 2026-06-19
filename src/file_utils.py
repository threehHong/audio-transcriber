from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TextIO


def ensure_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_timestamp(seconds: float) -> str:
    total_milliseconds = max(0, int(round(seconds * 1000)))
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def format_clock(seconds: float) -> str:
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"


def save_txt(segments: list[dict], output_path: str | Path) -> None:
    path = Path(output_path)
    with path.open("w", encoding="utf-8") as txt_file:
        for segment in segments:
            text = segment["text"].strip()
            if text:
                txt_file.write(f"{text}\n")


def save_srt(segments: list[dict], output_path: str | Path) -> None:
    path = Path(output_path)
    with path.open("w", encoding="utf-8") as srt_file:
        for index, segment in enumerate(segments, start=1):
            text = segment["text"].strip()
            if not text:
                continue
            srt_file.write(f"{index}\n")
            srt_file.write(
                f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}\n"
            )
            srt_file.write(f"{text}\n\n")


@dataclass
class IncrementalTranscriptWriter:
    output_dir: str | Path
    base_name: str

    def __post_init__(self) -> None:
        self.output_dir = ensure_output_dir(self.output_dir)
        self.txt_path = Path(self.output_dir) / f"{self.base_name}.txt"
        self.srt_path = Path(self.output_dir) / f"{self.base_name}.srt"
        self._txt_file: TextIO | None = None
        self._srt_file: TextIO | None = None
        self._segment_index = 0

    def __enter__(self) -> "IncrementalTranscriptWriter":
        self._txt_file = self.txt_path.open("w", encoding="utf-8")
        self._srt_file = self.srt_path.open("w", encoding="utf-8")
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        if self._txt_file is not None:
            self._txt_file.close()
        if self._srt_file is not None:
            self._srt_file.close()

    def write_segment(self, segment: dict) -> None:
        text = str(segment["text"]).strip()
        if not text:
            return

        if self._txt_file is None or self._srt_file is None:
            raise RuntimeError("출력 파일이 열려 있지 않습니다.")

        self._segment_index += 1
        self._txt_file.write(f"{text}\n")
        self._txt_file.flush()

        self._srt_file.write(f"{self._segment_index}\n")
        self._srt_file.write(
            f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}\n"
        )
        self._srt_file.write(f"{text}\n\n")
        self._srt_file.flush()
