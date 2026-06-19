from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterator

from config import COMPUTE_TYPE, DEVICE, LANGUAGE, MODEL_SIZE


def _load_whisper_model(status_callback: Callable[[str], None] | None = None):
    if status_callback is not None:
        status_callback(
            f"Whisper 모델 로딩 중: model={MODEL_SIZE}, device={DEVICE}, compute_type={COMPUTE_TYPE}"
        )

    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper가 설치되어 있지 않습니다. `pip install -r requirements.txt`를 실행해주세요."
        ) from exc

    try:
        return WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    except Exception as exc:
        raise RuntimeError(f"Whisper 모델을 로딩하지 못했습니다: {exc}") from exc


@dataclass
class TranscriptionSession:
    duration: float | None
    segments: Iterator[dict]


def transcribe_segments(
    file_path: str,
    status_callback: Callable[[str], None] | None = None,
) -> TranscriptionSession:
    model = _load_whisper_model(status_callback=status_callback)

    try:
        if status_callback is not None:
            status_callback("오디오 분석 및 전사 준비 중")
        segments, info = model.transcribe(
            file_path,
            language=LANGUAGE,
            vad_filter=True,
        )
    except Exception as exc:
        message = str(exc).lower()
        if "ffmpeg" in message:
            raise RuntimeError(
                "ffmpeg를 찾을 수 없습니다. ffmpeg 설치 후 시스템 PATH를 확인해주세요."
            ) from exc
        if "decode" in message or "invalid data" in message:
            raise RuntimeError(
                "오디오 파일을 디코딩하지 못했습니다. 파일 손상 여부와 ffmpeg 설치 상태를 확인해주세요."
            ) from exc
        raise RuntimeError(f"음성 전사 중 오류가 발생했습니다: {exc}") from exc

    def iter_segments() -> Iterator[dict]:
        for segment in segments:
            yield {
                "start": float(segment.start),
                "end": float(segment.end),
                "text": segment.text.strip(),
            }

    duration = getattr(info, "duration", None)
    if duration is not None:
        duration = float(duration)

    return TranscriptionSession(duration=duration, segments=iter_segments())


def transcribe_audio(file_path: str) -> list[dict]:
    session = transcribe_segments(file_path)
    return list(session.segments)
