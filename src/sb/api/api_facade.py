# Facade -> API interna
from sb import acervo
from sb import emprestimo as ge
from sb import gestao_usuarios as gu


def inicializar_sistema():
    '''
        Função chamada uma única vez para popular o backend
    '''

    gu.inicializar_admin_padrao()

    # Dados de exemplo
    livro_1, _ = acervo.cadastrar_livro("O Senhor dos Anéis", "J.R.R. Tolkien", "HarperCollins")
    acervo.add_copias(livro_1["ID_Livro"], 3, "Corredor 1-A")
    
    livro_2, _ = acervo.cadastrar_livro("Duna", "Frank Herbert", "Editora Aleph")
    acervo.add_copias(livro_2["ID_Livro"], 2, "Corredor 1-B")
    
    cliente_1, _ = gu.cadastrar_cliente("Ana Silva", "111", "Rua A", "9999", "ana123")
    gu.cadastrar_funcionario("func_comum", "123", "Comum")
    

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