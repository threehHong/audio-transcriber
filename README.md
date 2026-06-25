# Audio Transcriber

로컬 환경에서 음성 파일을 텍스트와 SRT 자막 파일로 변환하는 Python 기반 전사 프로그램입니다.

faster-whisper를 활용하여 긴 음성 파일도 안정적으로 텍스트 및 SRT 자막으로 변환할 수 있습니다.

회의록 작성, 인터뷰 전사, 음성 메모 기록화 등 다양한 음성 데이터를 텍스트로 변환해야 하는 업무에 활용할 수 있습니다.

## 주요 기능

- 음성 파일을 텍스트 파일(`.txt`)로 저장
- 음성 파일을 자막 파일(`.srt`)로 저장
- 세그먼트 단위 즉시 저장으로 장시간 파일 처리 지원

## 지원 입력 형식

- `.mp3`
- `.wav`
- `.m4a`
- `.mp4`

## 프로젝트 구조

```text
audio-transcriber/
├── README.md
├── requirements.txt
├── .gitignore
├── main.py
├── config.py
├── input/
│   └── .gitkeep
├── output/
│   └── .gitkeep
└── src/
    ├── __init__.py
    ├── transcriber.py
    └── file_utils.py
```

## 요구 사항

- Python 3.10 이상 권장
- 일부 환경에서는 `ffmpeg`가 필요할 수 있음

## 설치

`requirements.txt`를 사용하는 방법:

```bash
pip install -r requirements.txt
```

`faster-whisper`를 직접 설치하는 방법:

```bash
pip install faster-whisper
```

## 환경 준비

### 1. Python 준비

- Python 3.10 이상을 권장합니다.
- Windows에서는 `python` 명령이 바로 동작하지 않을 수 있으니, 설치 후 터미널에서 `python --version` 또는 `py --version`으로 확인하세요.

### 2. ffmpeg 설치

일부 환경에서는 오디오 파일 디코딩을 위해 `ffmpeg`가 필요할 수 있습니다.

설치 후 아래 명령으로 확인합니다.

```bash
ffmpeg -version
```

`ffmpeg` 명령이 인식되지 않더라도 현재 환경이나 입력 파일에 따라 프로그램이 동작할 수 있습니다.
다만 실행 중 디코딩 오류가 발생하면 `ffmpeg` 설치 및 PATH 설정을 확인하세요.

### 3. NVIDIA GPU 사용 전 준비 (선택)

아래 설정으로 GPU 실행을 하려면:

```python
DEVICE = "cuda"
COMPUTE_TYPE = "float16"
```

CUDA 사용 가능한 NVIDIA GPU가 있어야 하고, Windows 기준으로는 보통 CUDA Toolkit 12가 설치되어 있어야 합니다.

설치 후에는 아래 항목도 함께 확인하세요.

- `nvidia-smi` 명령이 정상 동작하는지 확인
- `nvcc --version` 명령으로 CUDA Toolkit 12 설치 여부 확인
- 환경변수 `CUDA_PATH` 또는 `CUDA_HOME`이 CUDA 12 설치 경로를 가리키는지 확인
- `PATH`에 CUDA의 `bin` 경로가 포함되어 있는지 확인

예시:

```text
CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.0
CUDA_HOME=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.0
PATH=%CUDA_PATH%\bin
```

이미 PATH에 등록되어 있다면 별도 설정은 필요하지 않을 수 있습니다.
반대로 GPU가 있어도 CUDA Toolkit 또는 환경변수가 제대로 잡혀 있지 않으면 `DEVICE = "cuda"`로 변경해도 실행 중 CUDA 관련 오류가 발생할 수 있습니다.

## 실행 방법

1. 변환할 음성 파일을 `input/` 폴더에 넣습니다.
2. 아래와 같이 실행합니다.

```bash
python main.py input/meeting.mp3
```

다른 예시:

```bash
python main.py input/26.06.02.m4a
```

## 실행 중 출력 예시

프로그램 시작 시:

```text
입력 파일 확인: meeting.mp3
전사 세션 초기화 중
Whisper 모델 로딩 중: model=medium, device=cpu, compute_type=int8
오디오 분석 및 전사 준비 중
변환 시작: 총 길이 00:50:12
첫 세그먼트를 기다리는 중
```

변환 진행 중:

```text
/ [##########--------------]  42.37% (00:21:15 / 00:50:12) | ETA 00:18:44 | 경과 00:13:39 | 세그먼트 128
```

표시 의미:

- 맨 앞 문자: 현재 갱신 중임을 보여주는 스피너
- `[####----]`: 전체 진행률을 시각적으로 보여주는 진행 바
- `진행률`: 전체 오디오 기준 처리 비율
- `(처리된 길이 / 전체 길이)`: 현재까지 전사된 오디오 길이
- `ETA`: 현재 속도 기준 예상 남은 시간
- `경과`: 실제 실행 후 지난 시간
- `세그먼트`: 저장된 세그먼트 개수

## 출력 결과

입력 파일명이 `meeting.mp3`라면 아래 파일이 생성됩니다.

- `output/meeting.txt`
- `output/meeting.srt`

TXT 예시:

```text
회의 시작하겠습니다.
오늘 모인 목적은 현재 발생한 [이슈 내용]의 원인 분석 및 해결 방안을 도출하기 위함입니다.
```

SRT 예시:

```text
1
00:00:00,000 --> 00:00:05,200
회의 시작하겠습니다.
```

## 설정 방법

프로그램 설정은 [config.py](C:/Users/threeh/Desktop/repo_fivetek/audio-transcriber/config.py:1)에서 관리합니다.

현재 기본값은 아래와 같습니다.

```python
MODEL_SIZE = "medium"
LANGUAGE = "ko"
DEVICE = "cpu"
COMPUTE_TYPE = "int8"
```

### 설정 파일 항목 설명

- `MODEL_SIZE`: Whisper 모델 크기
- `LANGUAGE`: 전사 언어, 기본값은 한국어 `ko`
- `DEVICE`: 실행 장치, 기본값은 `cpu`
- `COMPUTE_TYPE`: 연산 타입

추가 경로 설정:

```python
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4"}
```

- `INPUT_DIR`: 입력 파일을 둘 기본 폴더
- `OUTPUT_DIR`: 변환 결과가 저장되는 폴더
- `SUPPORTED_EXTENSIONS`: 허용된 입력 파일 확장자 목록

### 항목별 상세 가이드

#### `MODEL_SIZE`

Whisper 모델 크기입니다. 일반적으로 모델이 클수록 정확도가 좋아지지만 더 느립니다.

추천 기준:

- `small`: CPU 환경에서 속도를 가장 우선할 때
- `medium`: CPU 환경에서 속도와 정확도 균형
- `large-v3`: 정확도를 더 우선할 때, 다만 CPU에서는 많이 느릴 수 있음

#### `LANGUAGE`

전사 언어 코드입니다.

- 한국어 위주 파일이면 `ko`
- 언어가 명확하지 않거나 자동 감지를 기대한다면 모델 동작 방식에 맞춰 별도 조정이 필요할 수 있음

현재 프로젝트는 한국어 회의 녹음 용도에 맞춰 `ko`를 기본값으로 두고 있습니다.

#### `DEVICE`

전사를 어느 장치에서 수행할지 정합니다.

- `cpu`: 별도 GPU 없이 실행 가능
- `cuda`: NVIDIA GPU 사용 시 선택

GPU가 없다면 `cpu`를 사용해야 합니다.

#### `COMPUTE_TYPE`

모델 연산 방식입니다. 장치와 함께 조합해서 설정합니다.

대표 조합:

- CPU: `int8`
- NVIDIA GPU: `float16`

장치와 맞지 않는 값을 사용하면 모델 로딩 단계에서 오류가 날 수 있습니다.

### 추천 설정 조합

#### 1. 일반적인 CPU 환경

가장 무난한 시작점입니다.

```python
MODEL_SIZE = "medium"
LANGUAGE = "ko"
DEVICE = "cpu"
COMPUTE_TYPE = "int8"
```

추천 상황:

- 노트북 또는 일반 PC
- 긴 회의 파일 처리
- 속도와 정확도 균형이 필요할 때

#### 2. 속도 우선 CPU 환경

처리 시간이 너무 길다면 먼저 이 조합을 시도해보면 좋습니다.

```python
MODEL_SIZE = "small"
LANGUAGE = "ko"
DEVICE = "cpu"
COMPUTE_TYPE = "int8"
```

추천 상황:

- 긴 파일이 너무 오래 걸릴 때
- 정확도보다 처리 속도가 더 중요할 때

#### 3. GPU 사용 환경

NVIDIA GPU를 사용할 수 있다면 가장 빠르게 처리할 수 있는 선택지입니다.

```python
MODEL_SIZE = "medium"
LANGUAGE = "ko"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"
```

이 설정은 CUDA 사용 환경이 먼저 준비되어 있어야 정상 동작합니다.
Windows에서는 보통 CUDA Toolkit 12 설치와 `CUDA_PATH`/`CUDA_HOME`, `PATH` 설정 확인이 필요합니다.
자세한 내용은 위의 `환경 준비 > 3. NVIDIA GPU 사용 전 준비 (선택)`을 참고하세요.

추천 상황:

- CUDA 사용 가능한 NVIDIA GPU가 있을 때
- 장시간 파일을 더 빠르게 처리하고 싶을 때

### 설정 변경 절차

1. [config.py](C:/Users/threeh/Desktop/repo_fivetek/audio-transcriber/config.py:1)를 엽니다.
2. `MODEL_SIZE`, `LANGUAGE`, `DEVICE`, `COMPUTE_TYPE` 값을 원하는 조합으로 수정합니다.
3. 파일을 저장합니다.
4. 다시 아래 명령으로 실행합니다.

```bash
python main.py input/meeting.mp3
```

### 어떤 설정부터 바꾸면 좋은가

가장 체감 효과가 큰 순서는 보통 아래와 같습니다.

1. `MODEL_SIZE`를 줄이기
2. 가능하면 `DEVICE`를 `cuda`로 바꾸기
3. 장치에 맞는 `COMPUTE_TYPE`으로 조정하기

즉, 느릴 때는 먼저 `medium -> small` 순으로 줄여보는 것이 가장 간단합니다.

## 속도 관련 안내

긴 파일은 처리 시간이 꽤 걸릴 수 있습니다.  
특히 CPU 환경에서는 모델 크기에 따라 체감 속도 차이가 큽니다.

속도를 더 높이고 싶다면:

- CPU 사용 시 `MODEL_SIZE`를 `small` 또는 `medium`으로 조정
- NVIDIA GPU 사용 가능 시 `DEVICE = "cuda"`로 변경
- GPU 사용 시 `COMPUTE_TYPE = "float16"` 고려

예시:

```python
MODEL_SIZE = "medium"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"
```

## 예외 처리

다음 상황에서 원인을 알 수 있는 메시지를 출력합니다.

- 입력 파일이 존재하지 않는 경우
- 지원하지 않는 파일 확장자인 경우
- `faster-whisper`가 설치되지 않은 경우
- 일부 환경에서 `ffmpeg`가 필요하지만 설치되지 않았거나 PATH에 없는 경우
- 오디오 파일 디코딩에 실패한 경우
- 전사 중 기타 오류가 발생한 경우

## 주의 사항

- 프로그램을 중간에 종료한 뒤 다시 실행하면 처음부터 다시 전사합니다.
- 현재 버전은 이어받기(resume)를 지원하지 않습니다.
- 같은 이름으로 다시 실행하면 기존 `output/*.txt`, `output/*.srt` 파일을 덮어씁니다.

## 향후 개선 아이디어

- 이어받기 기능
- 화자 분리
- 회의 요약
- 주요 결정사항 추출
- 할 일 목록 추출
