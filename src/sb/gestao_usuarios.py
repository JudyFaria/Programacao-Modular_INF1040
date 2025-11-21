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
from src.sb import emprestimo
from src.sb import persistence

'''
    Em python, sem classe, nãoconsigo fazer uma "struct". Então vou usar um dicionário para agrupar 
'''

_loaded_state = persistence.load("gestao_usuarios", {})

_lst_funcionarios = _loaded_state.get("_lst_funcionarios", [])
_lst_clientes = _loaded_state.get("_lst_clientes", [])

_prox_id_funcionario = _loaded_state.get("_prox_id_funcionario", 1)
_prox_id_cliente = _loaded_state.get("_prox_id_cliente", 1) #contador para gerar os ids automaticamente


def _gerar_hash_senha(senha):
    '''
        Função auxiliar para gerar um hash SHA256 estável
    '''

    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def cadastrar_funcionario(nome, senha, papel):
    
    '''
        Cria um novo funcionário, adicionando-o a lista e retornando o dicionário
    '''

    global _prox_id_funcionario, _lst_funcionarios # utilizando variável global


    novo_func = {
        "ID_Funcionario": _prox_id_funcionario,
        "NomeUsuario": nome,
        "SenhaHash": _gerar_hash_senha(senha),
        "Papel": papel
    }

    _lst_funcionarios.append(novo_func) # addicionando na lista 
    _prox_id_funcionario += 1

    # persist changes
    persistence.save("gestao_usuarios", {
        "_lst_funcionarios": _lst_funcionarios,
        "_lst_clientes": _lst_clientes,
        "_prox_id_funcionario": _prox_id_funcionario,
        "_prox_id_cliente": _prox_id_cliente,
    })

    return novo_func

def cadastrar_cliente(nome, cpf, endereco, tel, senha):
    
    '''
        Cria um novo cliente, adicionando-o a lista e retornando o dicionário
    '''
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

    # persist changes
    persistence.save("gestao_usuarios", {
        "_lst_funcionarios": _lst_funcionarios,
        "_lst_clientes": _lst_clientes,
        "_prox_id_funcionario": _prox_id_funcionario,
        "_prox_id_cliente": _prox_id_cliente,
    })

    return novo_cliente


def inicializar_admin_padrao():
    '''
        Verifica se a lista de funcionários está vazia
        Se estiver, cria o administrador padrão 
    '''

    if len(_lst_funcionarios) == 0:
        cadastrar_funcionario("admin", "admin123", "Administrador")
        # cadastrar_funcionario already persists the change


def excluir_cliente(cpf):

    '''
        Busca o cliente pelo Id e remove da lista
        Verificando antes se o cliente possui empréstimos pendentes
        Retorna True se foi excluído, False se não foi encontrado ou se tem pendências
    '''
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
    tem_pendencias = False

    for emprestimo in ge._lst_emprestimos:
        if (emprestimo.get("ID_Cliente_Referencia") == id_cliente
            and emprestimo.get("Status") != "Finalizado"
        ):
            tem_pendencias = True
            break

    if tem_pendencias:
        print(f"Erro! Cliente {cliente_encontrado['Nome']} (CPF: {cpf}) não pode ser excluído pois tem empréstimos pendentes.")
        return False
    
    # Foi encontrado e não tem pendencias
    _lst_clientes.remove(cliente_encontrado)
    print(f"Excluido: Cliente: {cliente_encontrado['Nome']} | (CPF: {cpf})")
    # persist changes
    persistence.save("gestao_usuarios", {
        "_lst_funcionarios": _lst_funcionarios,
        "_lst_clientes": _lst_clientes,
        "_prox_id_funcionario": _prox_id_funcionario,
        "_prox_id_cliente": _prox_id_cliente,
    })
    return True


def autenticar(usuario, senha):
    '''
        Verifica as credencias nas listas de funcionarios e clientes
        Para funcionários, 'usuario' é o 'NomeUsuario'
        Para cliente, o'usuario' é o 'CPF'
        Retorna um dicionário com os dados do usuário ou None se falhar
    '''
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
                "Token": f"TOKEN_FUNC_{funcionario["ID_Funcionario"]}", # token simulado
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
                "Token": f"TOKEN_CLIENTE_{cliente["ID_Cliente"]}", # token simulado
                "Nome": cliente["Nome"]
            }
        
    # não achou 
    return None

# funções auxiliares para frontend
def get_todos_clientes():
    return _lst_clientes

def get_todos_funcionarios():
    return _lst_funcionarios