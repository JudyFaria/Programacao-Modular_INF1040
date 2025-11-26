import pytest 
import importlib
import src.sb.gestao_usuarios as gu
import src.sb.persistence as persistence
import src.sb.emprestimo as ge
import src.sb.acervo as acervo


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
    """
    Não deve ser possivel excluir um cliente com
    empréstimo pendente.
    """

    # 1. Cadastra cliente
    cliente = gu.cadastrar_cliente("Duda", "333", "Rua D", "666", "duda123")

    # 2. Cadastra um livro e uma cópia desse livro
    livro = acervo.cadastrar_livro("Livro Pendência", "Autor", "Ed")
    copias = acervo.add_copias(livro["ID_Livro"], 1, "Estante X")
    copia = copias[0]

    # 3. Cria um empréstimo EM ANDAMENTO para esse cliente
    emp = ge.criar_emprestimo(cliente["ID_Cliente"], copia["ID_Copia"])

    # Garantias de pré-condição (opcional, só pra sanity check)
    assert emp is not None
    assert emp["Status"] == "Em andamento"

    # 4. Tenta excluir o cliente
    exclusao = gu.excluir_cliente(cliente["CPF"])

    # 5. Verificações
    # Exclusão deve falhar por causa do empréstimo pendente
    assert exclusao is False

    # Cliente continua cadastrado
    clientes_restantes = gu.get_todos_clientes()
    assert any(c["CPF"] == cliente["CPF"] for c in clientes_restantes)
