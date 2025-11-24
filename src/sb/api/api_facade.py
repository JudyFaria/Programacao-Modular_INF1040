# Facade -> API interna
import src.sb.acervo as acervo
import src.sb.emprestimo as ge
import src.sb.gestao_usuarios as gu
import src.sb.multa as multa

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
    ge.verificar_e_atualizar_atrasos()

# Wrappers - Gestão de Usuário
def autenticar_usuario(usuario, senha):
    return gu.autenticar(usuario, senha)

def cadastrar_cliente(nome, cpf, endereco, tel, senha):
    res = gu.cadastrar_cliente(nome, cpf, end, tel, senha)
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

def get_todos_livros():
    return acervo.get_todos_livros()

def get_todas_copias():
    return acervo.get_todas_copias()


# Wrappers - Empréstimo 

def criar_emprestimo(id_cliente, id_copia):
    res = ge.criar_emprestimo(id_cliente, id_copia)
    if res: return True, f"Empréstimo {res['ID_Emprestimo']} criado!"
    return False, "Erro: Regras de negócio impediram o empréstimo."


def registrar_devolucao(id_copia):
    res = ge.registrar_devolucao(id_copia)
    if res: return True, "Devolução realizada."
    return False, "Erro: Nenhum empréstimo ativo para esta cópia."


def renovar_emprestimo(id_emprestimo, tipo_usuario):
    if ge.renovar_emprestimo(id_emprestimo, tipo_usuario): return True, "Renovado."
    return False, "Erro na renovação."


def get_historico_cliente(id_cliente):
    return ge.get_historico_cliente(id_cliente)


# --- FUNÇÕES AUXILIARES DE LEITURA (Para o Front-End) ---

def buscar_cliente_por_cpf(cpf):
    ''' 
        Busca um cliente na lista de usuários pelo CPF.
        Retorna o dicionário do usuário ou None.
    '''
    clientes = gu.get_todos_clientes()

    for usuario in clientes:
        print(usuario)
        if usuario.get("CPF") == cpf :
            return usuario
    
    return None

def get_copia_por_id(id_copia):
    ''' 
        Cruza informações de Cópia e Livro para exibição na UI.
        Acessa dados apenas através das funções públicas (getters).
    '''
    todas_copias = acervo.get_todas_copias()
    todos_livros = acervo.get_todos_livros()
    
    copia_alvo = None
    for c in todas_copias:
        if c["ID_Copia"] == id_copia:
            copia_alvo = c.copy() # Copia para não alterar o original
            break
            
    if copia_alvo:
        # Busca o título correspondente
        titulo = "Desconhecido"
        for l in todos_livros:
            if l["ID_Livro"] == copia_alvo["ID_Livro_Referencia"]:
                titulo = l["Titulo"]
                break
        copia_alvo["Titulo_Livro"] = titulo
        return copia_alvo
        
    return None

def get_copias_disponiveis_simples():
    ''' 
        Gera um relatório simples de cópias disponíveis.
        Usa getters para acessar acervo.
    '''
    todas_copias = acervo.get_todas_copias()
    todos_livros = acervo.get_todos_livros()
    
    resultado = []
    for c in todas_copias:
        if c["Status"] == "Disponível":
            # Encontra o título (next com valor default)
            titulo = next((l["Titulo"] for l in todos_livros if l["ID_Livro"] == c["ID_Livro_Referencia"]), "Indefinido")
            
            resultado.append({
                "ID": c["ID_Copia"],
                "Titulo": titulo,
                "Localizacao": c["LocalizacaoFisica"]
            })
    return resultado