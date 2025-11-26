# NÃO PODE CRIAR CLASSES


# Funcionário:
#     ID_Funcionario (Inteiro, Chave Primária)
#     NomeUsuario (Texto, Único)
#     SenhaHash (Texto)
#     Papel (Texto, ex: "Administrador")

# Cliente (Usuário da Biblioteca):
#     ID_Cliente (Inteiro, Chave Primária)
#     Nome (Texto)
#     CPF (Texto, Único)
#     Endereco (Texto)
#     Telefone (Texto)
#     SenhaHash (Texto)

import hashlib
from src.sb import emprestimo as ge
from src.sb import persistence


_loaded_state = persistence.load("gestao_usuarios", {})

_lst_funcionarios = _loaded_state.get("_lst_funcionarios", [])
_lst_clientes = _loaded_state.get("_lst_clientes", [])

_prox_id_funcionario = _loaded_state.get("_prox_id_funcionario", 1)
_prox_id_cliente = _loaded_state.get("_prox_id_cliente", 1) #contador para gerar os ids automaticamente

def salvar_estado_usuarios() -> None:
    """
    Persiste o estado atual de funcionários e clientes no arquivo JSON.
    Deve ser chamada apenas no encerramento da aplicação.
    """
    persistence.save(
        "gestao_usuarios",
        {
            "_lst_funcionarios": _lst_funcionarios,
            "_lst_clientes": _lst_clientes,
            "_prox_id_funcionario": _prox_id_funcionario,
            "_prox_id_cliente": _prox_id_cliente,
        },
    )


def _gerar_hash_senha(senha: str) -> str:
    """
    Gera o hash SHA-256 de uma senha em texto plano.

    Parâmetros: 
        senha (str): Senha em texto plano fornecida pelo usuário.

    Retorna:
        str: Representação em hexadecimal do hash SHA-256 da senha.
    """

    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def cadastrar_funcionario(nome: str, senha: str, papel: str) -> dict:
    """
    Cadastra um novo funcionário no sistema.

    Parâmetros: 
        nome (str): Nome de usuário (login) do funcionário. Deve ser único.
        senha (str): Senha em texto plano (será armazenada como hash).
        papel (str): Papel do funcionário, por exemplo: "Administrador".

    Retorna:
        dict: Dicionário contendo os dados do funcionário cadastrado.
    """

    global _prox_id_funcionario, _lst_funcionarios # utilizando variável global


    novo_func = {
        "ID_Funcionario": _prox_id_funcionario,
        "NomeUsuario": nome,
        "SenhaHash": _gerar_hash_senha(senha),
        "Papel": papel
    }

    _lst_funcionarios.append(novo_func) # addicionando na lista 
    _prox_id_funcionario += 1

    return novo_func

def cadastrar_cliente(nome: str, cpf: str, endereco: str, tel: str, senha: str) -> dict | None:
    """
    Cadastra um novo cliente no sistema.

    Parâmetros:
        nome (str): Nome completo do cliente.
        cpf (str): CPF do cliente (deve ser único).
        endereco (str): Endereço residencial.
        tel (str): Telefone de contato.
        senha (str): Senha em texto plano (será convertida em hash).

    Retorna:
        dict: Dicionário com os dados do cliente cadastrado, em caso de sucesso.
        None: Se já existir um cliente com o mesmo CPF.
    """

    global _prox_id_cliente, _lst_clientes

    for cliente in _lst_clientes:
        if cliente["CPF"] == cpf:
            print(f"Cliente de cpf: {cpf}, já cadastrado!")
            return None
        
    novo_cliente = {
        "ID_Cliente": _prox_id_cliente,
        "Nome": nome,
        "CPF": cpf,
        "Endereco": endereco,
        "Telefone": tel,
        "SenhaHash": _gerar_hash_senha(senha)
    }

    _lst_clientes.append(novo_cliente) 
    _prox_id_cliente += 1

    return novo_cliente


def inicializar_admin_padrao() -> None:
    """
        Cria um usuário administrador padrão, caso ainda não existam funcionários.

         Usuário criado (se necessário):
        - Nome de usuário: "admin"
        - Senha: "admin123"
        - Papel: "Administrador"
    """

    if len(_lst_funcionarios) == 0:
        cadastrar_funcionario("admin", "admin123", "Administrador")


def excluir_cliente(cpf: str) -> bool:

    """
    Exclui um cliente do sistema, se não houver emprestimos pendentes.

    Parâmetros:
        cpf (str): CPF do cliente a ser excluído.
        
    Retorna:
        bool: 
            - True se o cliente foi excluído com sucesso.
            - False em caso de erro, cliente inexistente ou pendências.
    """

    cliente_encontrado = None

    # acha o cliente na lista
    for cliente in _lst_clientes:

        if ( cliente["CPF"] == cpf):
            cliente_encontrado = cliente
            break

    if not cliente_encontrado:
        print(f"Erro! Cliente com CPF: {cpf} não encontrado")
        return False
    
    # procura pendências na lst de emprestimo
    id_cliente = cliente_encontrado["ID_Cliente"]
    
    # Pergunta ao módulo de empréstimo se ele tem pendências
    if ge.cliente_tem_pendencias(id_cliente):
        print(
            f"Erro! Cliente {cliente_encontrado['Nome']} (CPF: {cpf}) "
            "não pode ser excluído pois tem empréstimos pendentes."
        )
        return False
    
    # Não tem pendencias: pode excluir
    _lst_clientes.remove(cliente_encontrado)
    print(f"Excluido: Cliente: {cliente_encontrado['Nome']} | (CPF: {cpf})")
    
    return True


def autenticar(usuario: str, senha: str) -> dict | None:
    """
    Autentica um usuário (funcionário ou cliente) pelo nome de usuário/CPF e senha.

    Parâmetros:
        usuario (str): Nome de usuário (funcionário) ou CPF (cliente).
        senha (str): Senha em texto plano.

    Retorna:
        dict:
            Para funcionário:
                {
                    "Tipo": "Funcionario",
                    "ID": int,
                    "Papel": str,
                    "Token": str,
                    "Nome": str
                }

            Para cliente:
                {
                    "Tipo": "Cliente",
                    "ID": int,
                    "Token": str,
                    "Nome": str
                }

        None:
            Se a autenticação falhar (usuário não encontrado ou senha inválida).
"""

    # gera hash da senha fornecida para comparação
    senha_hash_comp = _gerar_hash_senha(senha)

    # funcionario
    for funcionario in _lst_funcionarios:
        if (funcionario["NomeUsuario"] == usuario
            and funcionario["SenhaHash"] == senha_hash_comp
        ):
            # retorna os dados
            return {
                "Tipo": "Funcionario",
                "ID": funcionario["ID_Funcionario"],
                "Papel": funcionario["Papel"],
                "Token": f"TOKEN_FUNC_{funcionario['ID_Funcionario']}", # token simulado
                "Nome" : funcionario["NomeUsuario"]
            }

    # cliente
    for cliente in _lst_clientes:
        if (cliente["CPF"] == usuario
            and cliente["SenhaHash"] == senha_hash_comp
        ):
            # retorna os dados
            return {
                "Tipo": "Cliente",
                "ID": cliente["ID_Cliente"],
                "Token": f"TOKEN_CLIENTE_{cliente['ID_Cliente']}", # token simulado
                "Nome": cliente["Nome"]
            }
        
    # Não encontrou usuário ou senha inválida
    return None

# funções auxiliares para frontend
def get_todos_clientes() -> list[dict]:
    """
    Obtém todos os clientes cadastrados.

    Retorna:
        list[dict]: Lista com todos os dicionários de clientes.
    """
    return _lst_clientes

def get_todos_funcionarios() -> list[dict]:
    """
    Obtém todos os funcionários cadastrados.

    Retorna:
        list[dict]: Lista com todos os dicionários de funcionários.
    """
    return _lst_funcionarios

def get_cliente_por_cpf(cpf: str) -> dict | None:
    """
    Busca e retorna um cliente específico pelo CPF.

    Parâmetros:
        cpf (str): CPF do cliente desejado.

    Retorna:
        dict | None:
            - Dicionário do cliente, se encontrado.
            - None se não existir cliente com esse CPF.
    """
    for cliente in _lst_clientes:
        if cliente["CPF"] == cpf:
            return cliente
    return None