import pytest 
import src.sb.gestao_usuarios as gu


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
    
    # Simula uma lista de empréstimos com uma pendência 
    _lista_emprestimos_ativo = [
        {
            "ID_Cliente_Referencia": cliente["ID_Cliente"], 
            "Status": "Em andamento"
        }
    ]
    
    assert len(gu._lst_clientes) == 1 # Garante que foi cadastrado
    
    exclusao = gu.excluir_cliente(cliente["CPF"])
    
    assert exclusao is False
    assert len(gu._lst_clientes) == 1 