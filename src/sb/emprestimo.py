# Empréstimo:
#     ID_Emprestimo (Inteiro, Chave Primária)
#     ID_Copia_Referencia (Chave Estrangeira para Copia)
#     ID_Cliente_Referencia (Chave Estrangeira para Cliente)
#     DataInicio (Data)
#     DataDevolucaoPrevista (Data)
#     DataDevolucaoReal (Data, nulo até a devolução)
#     Status (Texto: “Em andamento", "Atrasado", "Finalizado")

from datetime import date, timedelta
from src.sb import persistence

_loaded_state = persistence.load("emprestimo", {})

_lst_emprestimos = _loaded_state.get("_lst_emprestimos", [])
_prox_id_emprestimo = _loaded_state.get("_prox_id_emprestimo", 1)


# funções auxiliares

def salvar_alteracoes():
    '''
        Salva o estado atual no arquivo de persistência
    '''
    persistence.save("emprestimo", {
        "_lst_emprestimos": _lst_emprestimos,
        "_prox_id_emprestimo": _prox_id_emprestimo
    })

def _calcular_data_devolucao(data_inicio):
    ''' 
        Calcula 7 dias úteis após a data de início
        Ignorando Sabados e Domingos
        Retorna a data de devolução prevista 
    '''

    dias_adicionados = 0
    data_atual = data_inicio
    
    while dias_adicionados < 7:
        data_atual += timedelta(days=1)
        
        if data_atual.weekday() < 5: # 0-4 são dias úteis
            dias_adicionados += 1
    
    return data_atual

def verificar_e_atualizar_atrasos():
    '''
        Verifica se empréstimos em andamento estão atrasados
        e atualiza seu status conforme necessário.
    '''

    hoje = date.today()
    alterado = False

    for emp in _lst_emprestimos:
        if emp["Status"] == "Em andamento":

            # converte string ISO para date
            data_prevista = date.fromisoformat(emp["DataDevolucaoPrevista"])

            if hoje > data_prevista:
                emp["Status"] = "Atrasado"
                alterado = True

    if alterado:
        salvar_alteracoes()

#__________________________________________________

def criar_emprestimo(id_cliente, id_copia):
    '''
        Cria um novo empréstimo seguindo as regras de negócio:
        - Máximo 10 empréstimos ativos
        - Sem atrasos pendentes
        - Cópia deve estar disponível
    '''
    global _prox_id_emprestimo
    from src.sb import acervo # Importação local

    # 1. Atualiza status de atrasos antes de verificar
    verificar_e_atualizar_atrasos()

    # 2. Verifica regras do Cliente
    emprestimos_ativos = 0
    possui_atraso = False

    for emp in _lst_emprestimos:
        if emp["ID_Cliente_Referencia"] == id_cliente:
            if emp["Status"] in ["Em andamento", "Atrasado"]:
                emprestimos_ativos += 1
            if emp["Status"] == "Atrasado":
                possui_atraso = True
    
    if emprestimos_ativos >= 10:
        print(f"Erro: Cliente {id_cliente} atingiu o limite de 10 empréstimos.")
        return None
    
    if possui_atraso:
        print(f"Erro: Cliente {id_cliente} possui empréstimos atrasados.")
        return None

    # 3. Verifica e Obtém a Cópia do Acervo
    copia_encontrada = None
    for copia in acervo._lst_copias_livros:
        if copia["ID_Copia"] == id_copia:
            copia_encontrada = copia
            break
    
    if not copia_encontrada:
        print(f"Erro: Cópia {id_copia} não encontrada.")
        return None
    
    if copia_encontrada["Status"] != "Disponível":
        print(f"Erro: Cópia {id_copia} não está disponível.")
        return None

    # 4. Cria o Empréstimo
    data_hoje = date.today()
    data_prevista = _calcular_data_devolucao(data_hoje)

    novo_emprestimo = {
        "ID_Emprestimo": _prox_id_emprestimo,
        "ID_Copia_Referencia": id_copia,
        "ID_Cliente_Referencia": id_cliente,
        "DataInicio": data_hoje.isoformat(),
        "DataDevolucaoPrevista": data_prevista.isoformat(),
        "DataDevolucaoReal": None,
        "Status": "Em andamento"
    }

    _lst_emprestimos.append(novo_emprestimo)
    _prox_id_emprestimo += 1

    # 5. Atualiza o Acervo (Cópia vira 'Emprestado')
    copia_encontrada["Status"] = "Emprestado"
    
    # Persiste alteração no acervo
    persistence.save("acervo", {
        "_lst_livros": acervo._lst_livros,
        "_lst_copias_livros": acervo._lst_copias_livros,
        "_prox_id_livro": acervo._prox_id_livro,
        "_prox_id_copia": acervo._prox_id_copia,
    })

    # Persiste alteração no empréstimo
    salvar_alteracoes()

    return novo_emprestimo


def registrar_devolucao(id_copia):
    '''
        Registra a devolução de uma cópia, finalizando o empréstimo
        e liberando a cópia no acervo.
    '''
    from src.sb import acervo

    # 1. Encontrar o empréstimo ativo para esta cópia
    emprestimo_ativo = None
    for emp in _lst_emprestimos:
        if (emp["ID_Copia_Referencia"] == id_copia and 
            emp["Status"] in ["Em andamento", "Atrasado"]):
            emprestimo_ativo = emp
            break
    
    if not emprestimo_ativo:
        print(f"Erro: Nenhum empréstimo ativo encontrado para a cópia {id_copia}.")
        return None

    # 2. Atualizar o Empréstimo
    emprestimo_ativo["Status"] = "Finalizado"
    emprestimo_ativo["DataDevolucaoReal"] = date.today().isoformat()

    # 3. Atualizar o Acervo (Liberar a cópia)
    copia_encontrada = None
    for copia in acervo._lst_copias_livros:
        if copia["ID_Copia"] == id_copia:
            copia_encontrada = copia
            break
    
    if copia_encontrada:
        copia_encontrada["Status"] = "Disponível"
        # Persiste alteração no acervo
        persistence.save("acervo", {
            "_lst_livros": acervo._lst_livros,
            "_lst_copias_livros": acervo._lst_copias_livros,
            "_prox_id_livro": acervo._prox_id_livro,
            "_prox_id_copia": acervo._prox_id_copia,
        })

    # Persiste alteração no empréstimo
    salvar_alteracoes()

    print(f"Devolução registrada com sucesso para cópia {id_copia}.")
    return emprestimo_ativo

def renovar_emprestimo(id_emprestimo, tipo_usuario):
    '''
        Renova um empréstimo por mais 7 dias úteis.
        - Cliente não pode renovar se estiver atrasado.
        - Funcionário pode renovar atrasado (multa implícita).
    '''
    from src.sb import multa

    verificar_e_atualizar_atrasos()

    emprestimo = None
    for emp in _lst_emprestimos:
        if emp["ID_Emprestimo"] == id_emprestimo:
            emprestimo = emp
            break
    
    if not emprestimo:
        print(f"Erro: Empréstimo {id_emprestimo} não encontrado.")
        return False

    if emprestimo["Status"] == "Finalizado":
        print("Erro: Empréstimo já finalizado.")
        return False

    # Regras de Atraso
    if emprestimo["Status"] == "Atrasado":
        if tipo_usuario == "Cliente":
            print("Erro: Cliente não pode renovar item atrasado. Procure o balcão.")
            return False
            
        elif tipo_usuario == "Funcionario":
            multa_valor = multa.calcular_multa(emprestimo)
            
            # informa a multa 
            print(f"Aviso: Empréstimo está atrasado. Multa aplicada: R$ {multa_valor:.2f}")

            # pagamento da multa
            pago = multa.registrar_pagamento_multa(emprestimo["ID_Cliente_Referencia"], multa)
            if not pago:
                return False    
            
        print("Multa paga. Prosseguindo com a renovação.")

    # Calcula nova data
    data_atual_prevista = date.fromisoformat(emprestimo["DataDevolucaoPrevista"])
    nova_data = _calcular_data_devolucao(data_atual_prevista)
    
    emprestimo["DataDevolucaoPrevista"] = nova_data.isoformat()
    
    salvar_alteracoes()
    return True

def get_historico_cliente(id_cliente):
    '''
        Retorna todos os empréstimos de um cliente específico
    '''
    historico = []
    for emp in _lst_emprestimos:
        if emp["ID_Cliente_Referencia"] == id_cliente:
            historico.append(emp)
    return historico