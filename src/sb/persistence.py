import os
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _filepath(entity_name: str) -> str:
    return os.path.join(DATA_DIR, f"{entity_name}.json")


def load(entity_name: str, default=None):
    """Load persisted JSON for `entity_name` or return `default` if not present."""
    path = _filepath(entity_name)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default if default is not None else {}


def save(entity_name: str, data):
    """Atomically save `data` (JSON-serializable) for `entity_name`.

    Writes to a temporary file and replaces the target file to reduce
    the chance of corruption.
    """
    _ensure_dir()
    path = _filepath(entity_name)
    tmp_path = path + '.tmp'
    # Write to temp file first
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            # os.fsync may not be available in some environments
            pass
    # Atomic replace
    os.replace(tmp_path, path)
