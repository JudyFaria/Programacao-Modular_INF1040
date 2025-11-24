import datetime
from datetime import date
from src.sb import persistence

# --- Configurações da Multa ---
VALOR_BASE_MULTA = 5.00  # Valor fixo inicial ao atrasar (R$)
TAXA_DIARIA = 0.01       # Taxa de 1% ao dia (Juros Compostos)

# --- Carrega estado persistido ---
_loaded_state = persistence.load("multas", {})

_lst_pagamentos = _loaded_state.get("_lst_pagamentos", [])
_prox_id_pagamento = _loaded_state.get("_prox_id_pagamento", 1)

# --- Funções Auxiliares ---

def salvar_alteracoes():
    '''
        Salva o histórico de pagamentos
    '''
    persistence.save("multas", {
        "_lst_pagamentos": _lst_pagamentos,
        "_prox_id_pagamento": _prox_id_pagamento
    })

def calcular_dias_atraso(data_prevista_iso):
    '''
        Calcula quantos dias se passaram desde a data prevista até hoje.
    '''
    hoje = date.today()
    data_prevista = date.fromisoformat(data_prevista_iso)
    
    delta = hoje - data_prevista
    return delta.days

# --- Funções Principais ---

def calcular_multa(emprestimo):
    '''
        Calcula o valor da multa usando Juros Compostos (RF-024).
        Fórmula: M = P * (1 + i)^t
        Onde:
            P = Valor Base
            i = Taxa Diária
            t = Dias de Atraso
    '''
    if emprestimo["Status"] != "Atrasado":
        return 0.0
    
    dias_atraso = calcular_dias_atraso(emprestimo["DataDevolucaoPrevista"])
    
    if dias_atraso <= 0:
        return 0.0
    
    # Cálculo de Juros Compostos
    montante = VALOR_BASE_MULTA * ((1 + TAXA_DIARIA) ** dias_atraso)
    
    # Arredonda para 2 casas decimais
    return round(montante, 2)

def registrar_pagamento_multa(id_cliente, valor):
    '''
        Registra que uma multa foi paga pelo cliente.
        Isso permite que o empréstimo seja renovado (RF-026).
    '''
    global _prox_id_pagamento
    
    novo_pagamento = {
        "ID_Pagamento": _prox_id_pagamento,
        "ID_Cliente": id_cliente,
        "Valor": valor,
        "DataPagamento": date.today().isoformat()
    }
    
    _lst_pagamentos.append(novo_pagamento)
    _prox_id_pagamento += 1
    
    salvar_alteracoes()
    
    print(f"Pagamento de multa registrado: R$ {valor:.2f} (Cliente ID: {id_cliente})")
    return True

def obter_pagamentos_cliente(id_cliente):
    '''
        Retorna histórico de multas pagas por um cliente
    '''
    return [p for p in _lst_pagamentos if p["ID_Cliente"] == id_cliente]