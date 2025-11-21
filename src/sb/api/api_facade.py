# Facade -> API interna
from src.sb import acervo
from src.sb import emprestimo as ge
from src.sb import gestao_usuarios as gu


def inicializar_sistema():
    '''
        Função chamada uma única vez para popular o backend
    '''

    gu.inicializar_admin_padrao()

    # Dados de exemplo
    livro_1 = acervo.cadastrar_livro("O Senhor dos Anéis", "J.R.R. Tolkien", "HarperCollins")
    acervo.add_copias(livro_1["ID_Livro"], 3, "Corredor 1-A")
    
    livro_2 = acervo.cadastrar_livro("Duna", "Frank Herbert", "Editora Aleph")
    acervo.add_copias(livro_2["ID_Livro"], 2, "Corredor 1-B")
    
    cliente_1 = gu.cadastrar_cliente("Ana Silva", "111", "Rua A", "9999", "ana123")
    gu.cadastrar_funcionario("func_comum", "123", "Comum")
    
    # Verifica se algo venceu hoje
    ge.verificar_atrasos(ge._lst_emprestimos)

# Wrappers - Gestão de Usuário
def autenticar_usuario(usuario, senha):
    return gu.autenticar(usuario, senha)

def cadastrar_cliente(nome, cpf, endereco, tel, senha):
    return gu.cadastrar_cliente(nome, cpf, endereco, tel, senha)

def excluir_cliente(cpf):
    return gu.excluir_cliente(cpf)

def cadastrar_funcionario(nome, senha, papel):
    return gu.cadastrar_funcionario(nome, senha, papel)


# Wrappers - Acervo
def buscar_livro(termo):
    return acervo.buscar_livro(termo)

def get_todos_livros():
    return acervo.get_todos_livros()

def cadastrar_livro(titulo, autor, edicao):
    return acervo.cadastrar_livro(titulo, autor, edicao)

def add_copias(id_livro, qtd, loc):
    return acervo.add_copias(id_livro, qtd, loc)

def excluir_livro(id_livro):
    return acervo.excluir_livro_e_copias(id_livro)


# Wrappers - Empréstimo
def verificar_atrasos_no_inicio():
    """Chamado no startup para atualizar status"""
    ge.verificar_atrasos(ge._lst_emprestimos)

def criar_emprestimo(id_cliente, id_copia):
    (
        ge._lst_emprestimos, 
        acervo._lst_copias_livros, 
        ge._prox_id_emprestimo, 
        sucesso, 
        msg
    ) = ge.criar_emprestimo(
        id_cliente, 
        id_copia, 
        ge._lst_emprestimos, 
        acervo._lst_copias_livros, 
        ge._prox_id_emprestimo
    )
    return sucesso, msg

def registrar_devolucao(id_copia):
    (
        ge._lst_emprestimos,
        acervo._lst_copias_livros,
        sucesso,
        msg
    ) = ge.registrar_devolucao(
        id_copia,
        ge._lst_emprestimos,
        acervo._lst_copias_livros
    )
    return sucesso, msg

def renovar_emprestimo(id_emprestimo, tipo_usuario):
    (
        ge._lst_emprestimos,
        sucesso,
        msg
    ) = ge.renovar_emprestimo(
        id_emprestimo,
        tipo_usuario,
        ge._lst_emprestimos
    )
    return sucesso, msg

def get_historico_cliente(id_cliente):
    # Filtra apenas os empréstimos deste cliente
    todos = ge.get_todos_emprestimos()
    return [e for e in todos if e["ID_Cliente_Referencia"] == id_cliente]