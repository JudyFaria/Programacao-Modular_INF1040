# Facade -> API interna
import src.sb.acervo as acervo
import src.sb.emprestimo as ge
import src.sb.gestao_usuarios as gu
import src.sb.multa as multa
import atexit

# ------ FUNÇAO PARA SALVAR ESTADO DO SISTEMA ------

def salvar_estado_sistema():
    """
    Salva o estado de todos os módulos no disco.
    Pode ser chamada ao encerrar o sistema.
    """
    print(">> Salvando estado do sistema (atexit)...")
    acervo.salvar_estado_acervo()
    ge.salvar_estado_emprestimos()
    gu.salvar_estado_usuarios()
    multa.salvar_estado_multas()

atexit.register(salvar_estado_sistema)


def inicializar_sistema():
    '''
        Função chamada uma única vez para popular o backend.
        IDEMPOTENTE: não duplica dados se rodar múltiplas vezes.
    '''
    gu.inicializar_admin_padrao()

    # Verifica atrasos
    ge.verificar_e_atualizar_atrasos()


# Wrappers - Gestão de Usuário
def autenticar_usuario(usuario, senha):
    return gu.autenticar(usuario, senha)

def cadastrar_cliente(nome, cpf, endereco, tel, senha):
    res = gu.cadastrar_cliente(nome, cpf, endereco, tel, senha)
    if res: return f"Sucesso! Cliente {res['Nome']} cadastrado."
    return "Erro: CPF já existe."

def excluir_cliente(cpf):
    sucesso = gu.excluir_cliente(cpf)
    if sucesso: return True, "Cliente excluído."
    return False, "Erro: Cliente não encontrado ou com pendências."

def cadastrar_funcionario(nome, senha, papel):
    res = gu.cadastrar_funcionario(nome, senha, papel)
    if res: return f"Sucesso! {res['NomeUsuario']} cadastrado."
    return "Erro ao cadastrar."

def get_todos_clientes():
    return gu.get_todos_clientes()

def get_todos_funcionarios():
    return gu.get_todos_funcionarios()

def buscar_cliente_por_cpf(cpf):
    return gu.get_cliente_por_cpf(cpf)

# Wrappers - Acervo
def buscar_livro(termo):
    return acervo.buscar_livro(termo)

def cadastrar_livro(titulo, autor, editora):
    return acervo.cadastrar_livro(titulo, autor, editora)

def add_copias(id_livro, qtd, loc):
    return acervo.add_copias(id_livro, qtd, loc)

def excluir_livro(id_livro):
    return acervo.excluir_livro_e_copias(id_livro)

def get_todos_livros():
    return acervo.get_todos_livros()

def busca_copia_por_id(id_copia):
    return acervo.get_copia_por_id_com_titulo(id_copia)

def busca_copias_disponiveis_simples():
    return acervo.get_copias_disponiveis_simples()


# Wrappers - Empréstimo 

def criar_emprestimo(id_cliente, id_copia):
    res = ge.criar_emprestimo(id_cliente, id_copia)
    if res: return True, f"Empréstimo {res['ID_Emprestimo']} criado!"
    return False, "Erro: Regras de negócio impediram o empréstimo."


def registrar_devolucao(id_copia):
    res = ge.registrar_devolucao(id_copia)
    if res: return True, "Devolução realizada."
    return False, "Erro: Nenhum empréstimo ativo para este exemplar."


def renovar_emprestimo(id_emprestimo, tipo_usuario):
    if ge.renovar_emprestimo(id_emprestimo, tipo_usuario): return True, "Renovado."
    return False, "Erro na renovação."


def get_historico_cliente(id_cliente):
    return ge.get_historico_cliente(id_cliente)