import os
import random
import string
from pathlib import Path


def generate_random_string(length=32):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def _env_int(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return max(0, int(value))
    except ValueError:
        return default


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("CAFEBAZAAR_DATA_DIR", PROJECT_ROOT / "data")).expanduser().resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

RESULT_FILE = str(
    Path(os.getenv("CAFEBAZAAR_DB_PATH", DATA_DIR / "cafebazaar_results.db"))
    .expanduser()
    .resolve()
)

DEVICE_ID = generate_random_string()

# Polite delays between requests (milliseconds). Override with environment variables if needed.
SLEEP_AFTER_EACH_CATEGORIES_IN_MILL_SECONDS = _env_int("CAFEBAZAAR_CATEGORY_DELAY_MS", 10000)
SLEEP_AFTER_EACH_SUB_CATEGORIES_IN_MILL_SECONDS = _env_int("CAFEBAZAAR_SUBCATEGORY_DELAY_MS", 2000)
SLEEP_AFTER_EACH_APPS_IN_MILL_SECONDS = _env_int("CAFEBAZAAR_APP_DELAY_MS", 100)
