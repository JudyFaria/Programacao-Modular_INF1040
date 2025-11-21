import datetime
from datetime import date, timedelta

# Estado Global do Módulo
_lst_emprestimos = []
_prox_id_emprestimo = 1

# --- Funções Auxiliares (Lógica Interna) ---

def _calcular_data_devolucao(data_inicio):
    """
    Calcula 7 dias ÚTEIS após a data de início (RF-014).
    Ignora Sábados (5) e Domingos (6).
    """
    dias_adicionados = 0
    data_atual = data_inicio
    while dias_adicionados < 7:
        data_atual += timedelta(days=1)
        # weekday(): 0=Segunda, 4=Sexta, 5=Sábado, 6=Domingo
        if data_atual.weekday() < 5: 
            dias_adicionados += 1
    return data_atual

def _usuario_tem_pendencias(id_cliente, db_emprestimos):
    """
    Verifica se o usuário tem algum empréstimo 'Atrasado' (RF-015b).
    """
    for emp in db_emprestimos:
        if (emp["ID_Cliente_Referencia"] == id_cliente and 
            emp["Status"] == "Atrasado"):
            return True
    return False

def _contar_emprestimos_ativos(id_cliente, db_emprestimos):
    """
    Conta quantos empréstimos ativos o usuário tem.
    """
    contador = 0
    for emp in db_emprestimos:
        if (emp["ID_Cliente_Referencia"] == id_cliente and 
            emp["Status"] in ["Em andamento", "Atrasado"]):
            contador += 1
    return contador

# --- Funções Principais (Expostas) ---

def verificar_atrasos(db_emprestimos):
    """
    Atualiza automaticamente o status para 'Atrasado' se passou do prazo (RF-022).
    Deve ser chamada sempre que o sistema inicia ou carrega dados.
    """
    hoje = date.today()
    atualizados = 0
    
    # Como estamos modificando a lista, vamos iterar e modificar in-place
    for emp in db_emprestimos:
        if emp["Status"] == "Em andamento":
            if hoje > emp["DataDevolucaoPrevista"]:
                emp["Status"] = "Atrasado"
                atualizados += 1
    
    if atualizados > 0:
        print(f"Backend: {atualizados} empréstimos marcados como Atrasados.")
    
    return db_emprestimos

def criar_emprestimo(id_cliente, id_copia, db_emprestimos, db_copias, db_prox_id):
    """
    Registra um novo empréstimo (RF-013, RF-014, RF-015).
    Retorna: (nova_lista_emp, nova_lista_copias, novo_id, sucesso, msg)
    """
    # 1. Validar Cópia
    copia_alvo = None
    for copia in db_copias:
        if copia["ID_Copia"] == id_copia:
            copia_alvo = copia
            break
    
    if not copia_alvo:
        return db_emprestimos, db_copias, db_prox_id, False, "Erro: Cópia não encontrada."
    
    if copia_alvo["Status"] != "Disponível":
        return db_emprestimos, db_copias, db_prox_id, False, f"Erro: Cópia {id_copia} não está disponível (Status: {copia_alvo['Status']})."

    # 2. Validar Cliente (Regras de Negócio)
    # RF-015a: Limite de 10 empréstimos
    qtd_ativos = _contar_emprestimos_ativos(id_cliente, db_emprestimos)
    if qtd_ativos >= 10:
        return db_emprestimos, db_copias, db_prox_id, False, "Erro: Cliente atingiu o limite de 10 empréstimos ativos."

    # RF-015b: Pendências/Atrasos
    if _usuario_tem_pendencias(id_cliente, db_emprestimos):
        return db_emprestimos, db_copias, db_prox_id, False, "Erro: Cliente possui empréstimos ATRASADOS. Regularize para pegar novos livros."

    # 3. Criar o Empréstimo
    data_hoje = date.today()
    data_prevista = _calcular_data_devolucao(data_hoje) # RF-014

    novo_emprestimo = {
        "ID_Emprestimo": db_prox_id,
        "ID_Copia_Referencia": id_copia,
        "ID_Cliente_Referencia": id_cliente,
        "DataInicio": data_hoje,
        "DataDevolucaoPrevista": data_prevista,
        "DataDevolucaoReal": None,
        "Status": "Em andamento"
    }

    # 4. Atualizar Listas (Imutabilidade simulada: cria novas ou append)
    db_emprestimos.append(novo_emprestimo)
    
    # Atualiza status da cópia
    copia_alvo["Status"] = "Emprestado"
    
    msg = f"Sucesso: Empréstimo {db_prox_id} realizado. Devolução até {data_prevista.strftime('%d/%m/%Y')}."
    print(f"Backend: {msg}")
    
    return db_emprestimos, db_copias, db_prox_id + 1, True, msg

def registrar_devolucao(id_copia, db_emprestimos, db_copias):
    """
    Finaliza um empréstimo baseado no ID da cópia (RF-016).
    Retorna: (nova_lista_emp, nova_lista_copias, sucesso, msg)
    """
    # 1. Achar o empréstimo ativo para esta cópia
    emprestimo_alvo = None
    for emp in db_emprestimos:
        if (emp["ID_Copia_Referencia"] == id_copia and 
            emp["Status"] in ["Em andamento", "Atrasado"]):
            emprestimo_alvo = emp
            break
            
    if not emprestimo_alvo:
        return db_emprestimos, db_copias, False, "Erro: Não há empréstimo ativo para esta cópia."

    # 2. Achar a cópia para liberar
    copia_alvo = None
    for copia in db_copias:
        if copia["ID_Copia"] == id_copia:
            copia_alvo = copia
            break

    # 3. Finalizar
    emprestimo_alvo["DataDevolucaoReal"] = date.today()
    emprestimo_alvo["Status"] = "Finalizado"
    
    if copia_alvo:
        copia_alvo["Status"] = "Disponível"

    msg = f"Sucesso: Devolução registrada para Cópia {id_copia}."
    print(f"Backend: {msg}")
    return db_emprestimos, db_copias, True, msg

def renovar_emprestimo(id_emprestimo, tipo_usuario_solicitante, db_emprestimos):
    """
    Renova o prazo por mais 7 dias úteis (RF-017).
    Valida regras de atraso (RF-021, RF-026).
    Retorna: (nova_lista_emp, sucesso, msg)
    """
    emp_alvo = None
    for emp in db_emprestimos:
        if emp["ID_Emprestimo"] == id_emprestimo:
            emp_alvo = emp
            break
    
    if not emp_alvo:
        return db_emprestimos, False, "Empréstimo não encontrado."
    
    if emp_alvo["Status"] == "Finalizado":
        return db_emprestimos, False, "Este empréstimo já foi finalizado."

    # RF-021: Cliente não pode renovar se estiver atrasado
    if tipo_usuario_solicitante == "Cliente" and emp_alvo["Status"] == "Atrasado":
        return db_emprestimos, False, "Erro: Não é possível renovar via Portal do Cliente pois o item está atrasado. Procure um funcionário."

    # RF-026: Funcionário renovando atrasado (implica pagamento de multa)
    msg_extra = ""
    if emp_alvo["Status"] == "Atrasado" and tipo_usuario_solicitante == "Funcionario":
        msg_extra = " (Item estava atrasado. Multa deve ser cobrada)."
        emp_alvo["Status"] = "Em andamento" # Reseta status ao renovar

    # Aplica Renovação
    nova_data = _calcular_data_devolucao(emp_alvo["DataDevolucaoPrevista"])
    emp_alvo["DataDevolucaoPrevista"] = nova_data
    
    msg = f"Sucesso: Renovado até {nova_data.strftime('%d/%m/%Y')}{msg_extra}."
    return db_emprestimos, True, msg

def get_todos_emprestimos():
    return _lst_emprestimos