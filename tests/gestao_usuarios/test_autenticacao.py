import pytest 
import app.gestao_usuarios as gu


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


def test_autentica_funcionario_valido():
    '''
        ao fornecer credenciais válidas, 
        a função retorna o tipo de de usuário "Funcionário"
        e o token de sessao, diferenciando as permissoes de aceso
    '''

    funcionario = gu.cadastrar_funcionario("admin", "admin123", "Administrador")
    autenticacao = gu.autenticar(funcionario["NomeUsuario"], "admin123")

    assert autenticacao is not None
    assert autenticacao["Tipo"] == "Funcionario"
    assert autenticacao["Papel"] == "Administrador"
    assert "TOKEN_FUNC_1" in autenticacao["Token"]


def test_autentica_funcionario_invalido():
    '''
        Testa falha de login de funcionario (usuario ou senha)
    '''
    funcionario = gu.cadastrar_funcionario("admin", "admin123", "Administrador")
    
    autent_senha_errada = gu.autenticar(funcionario["NomeUsuario"], "senha_errada")
    autent_usuario_errado = gu.autenticar( "usuario-errado", "admin123")

    assert autent_senha_errada is None
    assert autent_usuario_errado is None


def test_autentica_cliente_valido():
    
    cliente = gu.cadastrar_cliente("Judy Faria", "123456", "Rua A", "99999-9999", "judy123")
    autenticacao = gu.autenticar(cliente["CPF"], "judy123")

    assert autenticacao is not None
    assert autenticacao["Tipo"] == "Cliente"
    assert autenticacao["ID"] == 1
    assert "TOKEN_CLIENTE_1" in autenticacao["Token"]


def test_autentica_cliente_invalido():
    
    cliente = gu.cadastrar_cliente("Judy Faria", "123456", "Rua A", "99999-9999", "judy123")
    
    autent_senha_errada = gu.autenticar(cliente["CPF"], "senha-errada")
    autent_usuario_errado = gu.autenticar("654321", "judy123")

    assert autent_senha_errada is None
    assert autent_usuario_errado is None