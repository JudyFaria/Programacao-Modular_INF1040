import pytest
import app.acervo as acervo

@pytest.fixture(autouse=True) # todos os testes rodam antes de executar
def setup_teste():
    '''
        Reseta as variáveis globais antes de cada teste
    '''
    acervo._lst_livros = []
    acervo._prox_id_livro = 1
    acervo._lst_copias_livros = []
    acervo._prox_id_copia = 1


def test_busca():
    
    livro_1 = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")  
    copia_1 = acervo.add_copias(livro_1["ID_Livro"], "Corredor 3, Prateleira A")
  

    livro_2 = acervo.cadastrar_livro("O Cavaleiro das Cruzadas", "Ana Seymour", "Nova Cultural")    
    copia_3 = acervo.add_copias(livro_2["ID_Livro"], "Corredor 3, Prateleira B")

    busca = acervo.buscar_livro("cruzada")
    
    assert isinstance (busca, list)
    assert len(busca) == 1
    assert busca[0]["Livro"]["Titulo"] == "O Cavaleiro das Cruzadas"

    

def test_busca_infos_iguais():
    livro_1 = acervo.cadastrar_livro("O Hobbit", "Tolkien", "Companhia Das Letras")  
    copia_1 = acervo.add_copias(livro_1["ID_Livro"], "Corredor 3, Prateleira A")
  

    livro_2 = acervo.cadastrar_livro("O Silmarillion", "Tolkien", "LaFonte")    
    copia_3 = acervo.add_copias(livro_2["ID_Livro"], "Corredor 3, Prateleira B")

    busca = acervo.buscar_livro("TOLKIEN")

    assert len(busca) == 2
    assert busca[0]["Livro"] != busca[1]["Livro"]


def test_busca_sem_resultado():
    livro_1 = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")  
    livro_2 = acervo.cadastrar_livro("O Silmarillion", "Tolkien", "LaFonte")   

    busca = acervo.buscar_livro("inexistente")

    assert isinstance(busca, list)
    assert len(busca) == 0


def test_busca_livro_sem_copias():
    livro_1 = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")  

    assert len(acervo._lst_copias_livros) == 0

    busca = acervo.buscar_livro("dona")

    assert len(busca) == 1
    assert isinstance(busca[0]["Copias"], list) 
    assert len(busca[0]["Copias"]) == 0

