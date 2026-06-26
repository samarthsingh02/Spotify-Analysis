from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA = BASE_DIR / "data" / "raw"
PROCESSED_DATA = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

MIN_PLAY_TIME_MS = 30000
SESSION_GAP_MINUTES = 30
TOP_N = 20