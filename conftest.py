# conftest.py na RAIZ do projeto
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent       # /workspaces/Programacao-Modular_INF1040
SRC_DIR = ROOT_DIR / "src"                       # /workspaces/.../src

src_str = str(SRC_DIR)
if src_str not in sys.path:
    sys.path.insert(0, src_str)
