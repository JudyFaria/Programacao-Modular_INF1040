import pytest
import src.sb.acervo as acervo

@pytest.fixture(autouse=True) # todos os testes rodam antes de executar
def setup_teste():
    '''
        Reseta as variáveis globais antes de cada teste
    '''
    acervo._lst_livros = []
    acervo._prox_id_livro = 1

def test_cadastra_livro_novo():
    livro_1 = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")

    # retornos
    assert isinstance(livro_1, dict)
    assert livro_1["ID_Livro"] == 1 #primeiro da lista
    assert livro_1["Titulo"] == "Senhora Dona do Baile"
    
    # estado global
    assert len(acervo._lst_livros) == 1
    assert acervo._lst_livros[0]["Titulo"] == "Senhora Dona do Baile"
    assert acervo._prox_id_livro == 2


def test_cadastra_livro_existente():  
    livro_1 = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")
    livro_2 = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")
    
    assert len(acervo._lst_livros) == 1
    assert livro_2["ID_Livro"] == 1
    assert acervo._prox_id_livro == 2


def test_cadastra_multiplos_livros():
    livro_1 = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")
    livro_2 = acervo.cadastrar_livro("O Cavaleiro das Cruzadas", "Ana Seymour", "Nova Cultural")
    livro_3 = acervo.cadastrar_livro("Estorvo", "Chico Buarque", "Companhia Das Letras")
    livro_4 = acervo.cadastrar_livro("Utopia", "Thomas More", "LaFonte")

    assert len(acervo._lst_livros) == 4 
    assert acervo._lst_livros[2]["Autor"] == "Chico Buarque"
    assert acervo._prox_id_livro == 5