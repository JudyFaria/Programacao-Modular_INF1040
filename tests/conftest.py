import importlib
import shutil
import sys
from pathlib import Path
import pytest

# Importe o módulo de persistência para poder alterar o caminho dele durante os testes
# Ajuste o import conforme o caminho real do seu projeto
try:
    import src.sb.persistence as persistence_module
except ImportError:
    persistence_module = None

def _data_dir():
    """
    Define o diretório de dados de teste.
    Agora aponta para: ./tests/data_test
    """
    # .parent pega a pasta onde este arquivo (conftest.py) está.
    return Path(__file__).resolve().parent / 'data_test'

def _remove_data_files():
    d = _data_dir()
    # Cria a pasta se não existir, para evitar erros
    d.mkdir(parents=True, exist_ok=True)
    
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
        'src.sb.multa',
    ]
    for m in modules:
        try:
            if m in sys.modules:
                importlib.reload(sys.modules[m])
        except Exception:
            pass

@pytest.fixture(autouse=True)
def clean_persistence_and_reload(monkeypatch):
    """
    1. Define o diretório de dados para 'tests/data_test'.
    2. Redireciona a persistência do sistema para usar essa pasta.
    3. Limpa arquivos antes e depois.
    4. Recarrega módulos para zerar memória RAM.
    """
    # 1. Define caminho de teste
    test_dir = _data_dir()
    
    # 2. Monkeypatch: Força o módulo de persistência a salvar na pasta de teste
    # Isso é CRUCIAL: sem isso, o teste limpa a pasta 'tests/data_test', 
    # mas o sistema continua salvando na pasta 'data' original na raiz.
    if persistence_module:
        monkeypatch.setattr(persistence_module, 'DATA_DIR', str(test_dir))

    # 3. Limpa a pasta de teste antes de começar
    _remove_data_files()
    
    # 4. Recarrega módulos (para limpar listas em memória _lst_...)
    _reload_sb_modules()
    
    yield
    
    # Limpeza opcional no final
    _remove_data_files()