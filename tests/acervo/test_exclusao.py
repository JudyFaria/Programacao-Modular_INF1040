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


def test_exclusao_livro_copias_disponiveis():
    livro = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")  
    copia_1 = acervo.add_copias(livro["ID_Livro"], "Corredor 3, Prateleira A")

    assert len(acervo._lst_copias_livros) == 1
    assert len(acervo._lst_livros) == 1
    assert copia_1["Status"] == "Disponível"
    
    exclusao = acervo.excluir_livro_e_copias(livro["ID_Livro"])

    assert len(acervo._lst_copias_livros) == 0
    assert len(acervo._lst_livros) == 0


def test_exclusao_livro_com_copia_emprestada():
    livro = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")
    
    copia_1 = acervo.add_copias(livro["ID_Livro"], "Corredor 3, Prateleira A")
    copia_2 = acervo.add_copias(livro["ID_Livro"], "Corredor 3, Prateleira A")
    copia_3 = acervo.add_copias(livro["ID_Livro"], "Corredor 3, Prateleira A")
    copia_4 = acervo.add_copias(livro["ID_Livro"], "Corredor 3, Prateleira A")

    copia_3["Status"] = "Emprestada"

    assert copia_3["Status"] != "Disponível"

    exclusao = acervo.excluir_livro_e_copias(livro["ID_Livro"])

    assert len(acervo._lst_livros) == 1
    assert len(acervo._lst_copias_livros) == 4


def test_exclusao_livro_id_inexistente():

    livro = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")  
    copia_1 = acervo.add_copias(livro["ID_Livro"], "Corredor 3, Prateleira A")

    assert len(acervo._lst_livros) == 1
    assert len(acervo._lst_copias_livros) == 1

    id_inexistente = 999
    exclusao = acervo.excluir_livro_e_copias(id_inexistente)

    assert exclusao == True
    assert len(acervo._lst_livros) == 1
    assert len(acervo._lst_copias_livros) == 1


def test_exclusao_nao_afeta_outros_livros():
    livro_1 = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")  
    copia_1 = acervo.add_copias(livro_1["ID_Livro"], "Corredor 3, Prateleira A")
    copia_2 = acervo.add_copias(livro_1["ID_Livro"], "Corredor 3, Prateleira A")


    livro_2 = acervo.cadastrar_livro("O Cavaleiro das Cruzadas", "Ana Seymour", "Nova Cultural")    
    copia_3 = acervo.add_copias(livro_2["ID_Livro"], "Corredor 3, Prateleira B")

    assert len(acervo._lst_livros) == 2
    assert len(acervo._lst_copias_livros) == 3

    exclusao = acervo.excluir_livro_e_copias(livro_1["ID_Livro"])

    assert exclusao == True
    assert len(acervo._lst_livros) == 1
    assert len(acervo._lst_copias_livros) == 1

    assert acervo._lst_livros[0]["Titulo"] == "O Cavaleiro das Cruzadas"
    assert acervo._lst_copias_livros[0]["ID_Livro_Referencia"] == livro_2["ID_Livro"]