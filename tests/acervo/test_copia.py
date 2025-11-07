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


def test_add_copia_livro_existente():
    '''
        Testa a adiçao de uma cópia de um livro existente
    '''

    livro = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")
    copia_1 = acervo.add_copias(livro["ID_Livro"], "Corredor 3, Prateleira A")

    assert isinstance(copia_1, dict)
    assert copia_1["ID_Livro_Referencia"] == livro["ID_Livro"]
    assert len(acervo._lst_copias_livros) > 0
    
    assert acervo._prox_id_copia == 2
    assert acervo._prox_id_livro == 2


def test_add_copia_livro_inexistente():
    '''
        Garante que não é adicionado cópias para livros não existentes
    '''

    copia_1 = acervo.add_copias(1, "Corredor 3, Prateleira A")

    assert len(acervo._lst_copias_livros) == 0



def test_status_add_copia():
    '''
        Garante que ao adicionar uma cópia
        o status começa com "Disponível"
    '''

    livro = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")
    copia_1 = acervo.add_copias(livro["ID_Livro"], "Corredor 3, Prateleira A")

    assert copia_1["Status"] == "Disponível"


def test_add_multiplas_copias_um_livro():
    '''
        Testa a adição de múltiplas cópias associadas a um título
        Cada um com:
            - identificador único
            - status de disponibilidade
    '''
   
    livro = acervo.cadastrar_livro("Senhora Dona do Baile", "Zélia Gattai", "Record")
    
    copia_1 = acervo.add_copias(livro["ID_Livro"], "Corredor 3, Prateleira A")
    copia_2 = acervo.add_copias(livro["ID_Livro"], "Corredor 3, Prateleira A")
    copia_3 = acervo.add_copias(livro["ID_Livro"], "Corredor 3, Prateleira A")
    copia_4 = acervo.add_copias(livro["ID_Livro"], "Corredor 3, Prateleira A")

    assert len(acervo._lst_copias_livros) == 4
    assert copia_1["ID_Livro_Referencia"] == copia_4["ID_Livro_Referencia"] 
    assert copia_1["ID_Copia"] != copia_4["ID_Copia"]

    for copia in acervo._lst_copias_livros:
        assert copia["Status"] == "Disponível"

    # tentando a unicidade dos ids
    ids_vistos = set()
    for copia in acervo._lst_copias_livros:
        id_atual = copia["ID_Copia"]
        
        assert id_atual not in ids_vistos, f"Id repetidos, não únicos!"
        ids_vistos.add(id_atual)




# dentro da listra de copias, se id ref igual, então id cópias diferentes


