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


'''
    Em python, sem classe, nãoconsigo fazer uma "struct". Então vou usar um dicionário para agrupar 
'''

_lst_funcionarios = []
_lst_clientes = []

_prox_id_funcionario = 1
_prox_id_cliente = 1 #contador para gerar os ids automaticamente


def cadastrar_funcionario(nome, senha, papel):
    
    '''
        Cria um novo funcionário, adicionando-o a lista e retornando o dicionário
    '''

    global _prox_id_funcionario, _lst_funcionarios # utilizando variável global

    novo_func = {
        "ID_Funcionario": _prox_id_funcionario,
        "NomeUsuario": nome,
        "SenhaHash": hash(senha),
        "Papel": papel
    }

    _lst_funcionarios.append(novo_func) # addicionando na lista 
    _prox_id_funcionario += 1

    return novo_func

def cadastrar_cliente(nome, cpf, endereco, tel, senha):
    
    '''
        Cria um novo cliente, adicionando-o a lista e retornando o dicionário
    '''
    global _prox_id_cliente, _lst_clientes

    novo_cliente = {
        "ID_Cliente": _prox_id_cliente,
        "Nome": nome,
        "CPF": cpf,
        "Endereço": endereco,
        "Telefone": tel,
        "SenhaHash": hash(senha)
    }

    _lst_clientes.append(novo_cliente) 
    _prox_id_cliente += 1

    return novo_cliente

def excluir_cliente(cpf):

    '''
        Busca o cliente pelo Id e remove da lista
        Retorna True se foi excluído, False se não foi encontrado.
    '''
    indice_excluir = -1

    # usando enumerate() para ter o índice e o dicionário do cliente
    for i, cliente in enumerate(_lst_clientes):

        if ( cliente["CPF"] == cpf):
            indice_excluir = i
            break

    if indice_excluir != -1:
        cliente_removido = _lst_clientes.pop(indice_excluir)
        print(f"Excluido: Cliente: {cliente_removido['Nome']} | (Id: {cpf})")
        return True
    
    else:
        print(f"Erro! Cliente com CPF: {cpf} não encontrado")
        return False