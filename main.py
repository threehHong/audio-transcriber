from __future__ import annotations

import argparse
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from config import OUTPUT_DIR, SUPPORTED_EXTENSIONS
from src.file_utils import IncrementalTranscriptWriter, ensure_output_dir, format_clock
from src.transcriber import transcribe_segments

PROGRESS_BAR_WIDTH = 24
SPINNER_FRAMES = ("|", "/", "-", "\\")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audio Transcriber: 음성 파일을 TXT와 SRT로 변환합니다."
    )
    parser.add_argument("input_file", help="변환할 음성 파일 경로")
    return parser.parse_args()


def validate_input_file(file_path: Path) -> Path:
    resolved_path = file_path.expanduser().resolve()

    if not resolved_path.exists() or not resolved_path.is_file():
        raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {resolved_path}")

    if resolved_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(
            f"지원하지 않는 파일 형식입니다: {resolved_path.suffix} (지원 형식: {supported})"
        )

    return resolved_path


def print_status(message: str) -> None:
    print(message, flush=True)


@dataclass
class ProgressState:
    total_duration: float | None
    started_at: float
    processed_seconds: float = 0.0
    segment_count: int = 0
    complete: bool = False
    frame_index: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)


class LiveProgressRenderer:
    def __init__(self, state: ProgressState, refresh_interval: float = 0.1) -> None:
        self.state = state
        self.refresh_interval = refresh_interval
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_render_width = 0

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
        self._render(final=True)
        print()

    def update(self, processed_seconds: float, segment_count: int) -> None:
        with self.state.lock:
            self.state.processed_seconds = processed_seconds
            self.state.segment_count = segment_count

    def mark_complete(self) -> None:
        with self.state.lock:
            self.state.complete = True
            if self.state.total_duration:
                self.state.processed_seconds = self.state.total_duration

    def _run(self) -> None:
        while not self._stop_event.is_set():
            self._render()
            time.sleep(self.refresh_interval)

    def _render(self, final: bool = False) -> None:
        with self.state.lock:
            processed_seconds = self.state.processed_seconds
            segment_count = self.state.segment_count
            total_duration = self.state.total_duration
            frame_index = self.state.frame_index
            complete = self.state.complete
            if not final:
                self.state.frame_index += 1

        elapsed_wall_time = max(time.monotonic() - self.state.started_at, 0.001)
        spinner = "OK" if complete or final else SPINNER_FRAMES[frame_index % len(SPINNER_FRAMES)]

        if total_duration and total_duration > 0:
            progress_ratio = min(processed_seconds / total_duration, 1.0)
            progress_percent = progress_ratio * 100
            filled = min(int(progress_ratio * PROGRESS_BAR_WIDTH), PROGRESS_BAR_WIDTH)
            progress_bar = f"[{'#' * filled}{'-' * (PROGRESS_BAR_WIDTH - filled)}]"
            if processed_seconds > 0:
                remaining_audio_seconds = max(total_duration - processed_seconds, 0.0)
                eta_seconds = remaining_audio_seconds * (elapsed_wall_time / processed_seconds)
                eta_text = format_clock(eta_seconds)
            else:
                eta_text = "--:--:--"
            message = (
                f"\r{spinner} {progress_bar} {progress_percent:6.2f}% "
                f"({format_clock(processed_seconds)} / {format_clock(total_duration)}) "
                f"| ETA {eta_text} "
                f"| 경과 {format_clock(elapsed_wall_time)} "
                f"| 세그먼트 {segment_count}"
            )
        else:
            message = (
                f"\r{spinner} 처리 중 {format_clock(processed_seconds)} "
                f"| 경과 {format_clock(elapsed_wall_time)} "
                f"| 세그먼트 {segment_count}"
            )

        padding = max(self._last_render_width - len(message), 0)
        print(f"{message}{' ' * padding}", end="", flush=True)
        self._last_render_width = len(message)


def main() -> int:
    args = parse_args()

    try:
        input_path = validate_input_file(Path(args.input_file))
        ensure_output_dir(OUTPUT_DIR)

        output_stem = input_path.stem
        writer = IncrementalTranscriptWriter(output_dir=OUTPUT_DIR, base_name=output_stem)

        print_status(f"입력 파일 확인: {input_path.name}")
        print_status("전사 세션 초기화 중")
        session = transcribe_segments(str(input_path), status_callback=print_status)
        total_duration = session.duration
        segment_count = 0
        started_at = time.monotonic()
        progress_state = ProgressState(total_duration=total_duration, started_at=started_at)
        progress_renderer = LiveProgressRenderer(progress_state)

        if total_duration:
            print(f"변환 시작: 총 길이 {format_clock(total_duration)}")
        else:
            print("변환 시작")

        print_status("첫 세그먼트를 기다리는 중")

        progress_renderer.start()
        try:
            with writer:
                for segment in session.segments:
                    writer.write_segment(segment)
                    segment_count += 1
                    progress_renderer.update(segment["end"], segment_count)
        finally:
            progress_renderer.mark_complete()
            progress_renderer.stop()

        print(f"전사 완료: {input_path.name}")
        print(f"TXT 저장: {writer.txt_path}")
        print(f"SRT 저장: {writer.srt_path}")
        print(f"세그먼트 수: {segment_count}")
        return 0
    except FileNotFoundError as exc:
        print(f"오류: {exc}", file=sys.stderr)
    except ValueError as exc:
        print(f"오류: {exc}", file=sys.stderr)
    except RuntimeError as exc:
        print(f"오류: {exc}", file=sys.stderr)
    except Exception as exc:
        print(f"예상치 못한 오류가 발생했습니다: {exc}", file=sys.stderr)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
