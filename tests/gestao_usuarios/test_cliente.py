import pytest 
import importlib
import src.sb.gestao_usuarios as gu
import src.sb.persistence as persistence
import src.sb.emprestimo as ge


@pytest.fixture(autouse=True) # todos os testes rodam antes de executar
def setup_teste():
    ''' 
        Reseta as listas globais do módulo gu antes de cada teste. 
    '''
    gu._lst_funcionarios = []
    gu._lst_clientes = []
    gu._prox_id_funcionario = 1
    gu._prox_id_cliente = 1

    gu.inicializar_admin_padrao()


def test_cadastro_cliente():
    '''
        Funcionário deve ser capaz de cadastrar novos clientes
    '''

    cliente = gu.cadastrar_cliente("Judy", "123456", "Rua A", "12345678", "judy123")

    assert len(gu._lst_clientes) == 1
    assert cliente["ID_Cliente"] == 1
    assert cliente["Endereco"] == "Rua A"
    assert gu._lst_clientes[0]["CPF"] == "123456"
    assert gu._prox_id_cliente == 2
    

def test_exclusao_cliente():
    cliente = gu.cadastrar_cliente("Carla", "222", "Rua C", "777", "carla123")
    _lista_emprestimos_vazia = []

    assert len(gu._lst_clientes) == 1

    exclusao = gu.excluir_cliente(cliente["CPF"])

    assert exclusao is True
    assert len(gu._lst_clientes) == 0
    


def test_exclusao_cliente_pendencia():
    '''
        Não deve ser possivel excluir um cliente com 
        empréstimo pendente
    '''

    cliente = gu.cadastrar_cliente("Duda", "333", "Rua D", "666", "duda123")
    
    # # Simula uma lista de empréstimos com uma pendência 
    # _lista_emprestimos_ativo = [
    #     {
    #         "ID_Cliente_Referencia": cliente["ID_Cliente"], 
    #         "Status": "Em andamento"
    #     }
    # ]

    # começa em andamento
    db_emp, db_copias, prox = emp.criar_emprestimo(1, 99, db_emp, db_copias, prox)
    emp = ge.criar_emprestimo( 
        cliente["ID_Cliente"], 
        1,  # id_copia
        "2024-07-01", 
        "2024-07-15",
        2
    )

    # alterando o status para o test
    emp["Status"] = "Em andamento"


    # Persiste a lista para que o módulo de empréstimos a carregue como estado global
    persistence.save("emprestimo", {
        "_lst_emprestimos": [emp],
        "_prox_id_emprestimo": 2,
    })

    # recarrega o módulo de empréstimo para que ele leia o arquivo de persistência
    importlib.reload(ge)
    
    assert len(gu._lst_clientes) == 1 # Garante que foi cadastrado
    assert len(ge._lst_emprestimos) == 1 # Garante que a lista de empréstimos foi carregada
    
    exclusao = gu.excluir_cliente(cliente["CPF"])  # não passa lista, usa o estado global do módulo de emprestimo
    
    assert exclusao is False
    assert len(gu._lst_clientes) == 1 