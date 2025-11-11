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



def test_cadastro_funcionario_por_administrador():
    '''
        Se, e somente se, usuário for "administrador"
        Deve ser capaz de cadastrar funciónarios 
    '''

    # simula login
    usuario_log = gu.autenticar("admin", "admin123")

    funcionario = None
    if ( usuario_log is not None 
        and usuario_log["Tipo"] == "Funcionario" 
        and usuario_log["Papel"] == "Administrador"
    ): 
        funcionario = gu.cadastrar_funcionario("novo_func", "func123", "Comun")

    assert funcionario is not None
    assert len(gu._lst_funcionarios) == 2
    assert funcionario["NomeUsuario"] == "novo_func"


def test_cadastro_funcionario_por_funcionario():
    '''
        Testa a regra de negócio
        Que diz que um funcionario só pode ser cadastrado por um admin
    '''
    funcionario_comun = gu.cadastrar_funcionario("func", "func123", "Comun")
    usuario_log = gu.autenticar(funcionario_comun["NomeUsuario"], "func123")

    novo_func = None
    if (usuario_log is not None
        and usuario_log["Tipo"] == "Funcionario" 
        and usuario_log["Papel"] == "Administrador"
    ): 
        novo_func = gu.cadastrar_funcionario("novo_func", "novofunc123", "Comun")

    assert novo_func is None
    assert len(gu._lst_funcionarios) == 2 #adim e funcionario comun



def test_inicializar_admin_padrao():
    ''' Testa se o admin padrão  criado corretamente '''

    # Reseta manualmente as listas (após o setup)
    gu._lst_funcionarios = []
    gu._prox_id_funcionario = 1
    
    assert len(gu._lst_funcionarios) == 0
   
    gu.inicializar_admin_padrao()
    
    assert len(gu._lst_funcionarios) == 1
    assert gu._lst_funcionarios[0]["NomeUsuario"] == "admin"
    assert gu._lst_funcionarios[0]["Papel"] == "Administrador"
    assert gu._lst_funcionarios[0]["ID_Funcionario"] == 1
    
    # chamar de novo não deve criar outro admin
    gu.inicializar_admin_padrao()
    assert len(gu._lst_funcionarios) == 1