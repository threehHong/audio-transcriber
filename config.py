from pathlib import Path

# MODEL_SIZE = "large-v3"
MODEL_SIZE = "medium"
LANGUAGE = "ko"
# DEVICE = "cpu"
# COMPUTE_TYPE = "int8"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4"}
