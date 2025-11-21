import importlib
import shutil
from pathlib import Path


def _data_dir():
    # repo root is two levels up from tests directory
    return Path(__file__).resolve().parents[1] / 'data'


def _remove_data_files():
    d = _data_dir()
    if d.exists() and d.is_dir():
        for p in d.glob('*.json'):
            try:
                p.unlink()
            except Exception:
                pass


def _reload_sb_modules():
    # modules to reload so they load fresh state from persistence
    modules = [
        'src.sb.acervo',
        'src.sb.gestao_usuarios',
        'src.sb.emprestimo',
    ]
    for m in modules:
        try:
            if m in __import__('sys').modules:
                importlib.reload(__import__(m, fromlist=['*']))
        except Exception:
            # ignore modules that can't be reloaded in some environments
            pass


import pytest


@pytest.fixture(autouse=True)
def clean_persistence_and_reload():
    """Ensure `data/` is empty and reload core modules before each test."""
    _remove_data_files()
    _reload_sb_modules()
    yield
    # optional cleanup after test
    _remove_data_files()
