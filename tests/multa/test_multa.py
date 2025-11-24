import pytest
from datetime import date, timedelta
import src.sb.multa as multa

# O conftest.py garante que o estado é resetado antes de cada teste.

# --- Testes de Cálculo de Multa (RF-024) ---

def test_calcular_multa_sem_atraso():
    """
    Empréstimo "Em andamento" ou "Finalizado" não deve gerar multa.
    """
    emprestimo_mock = {
        "Status": "Em andamento",
        "DataDevolucaoPrevista": date.today().isoformat()
    }
    
    valor = multa.calcular_multa(emprestimo_mock)
    assert valor == 0.0

def test_calcular_multa_com_atraso_simples():
    """
    Testa o cálculo básico.
    Fórmula: 5.00 * (1 + 0.01) ^ dias
    """
    # Simula 5 dias de atraso
    dias_atraso = 5
    data_prevista = (date.today() - timedelta(days=dias_atraso)).isoformat()
    
    emprestimo_mock = {
        "Status": "Atrasado",
        "DataDevolucaoPrevista": data_prevista
    }
    
    # Cálculo manual esperado: 5 * (1.01^5) = 5 * 1.05101 = 5.255... -> 5.26
    valor_calculado = multa.calcular_multa(emprestimo_mock)
    
    assert valor_calculado > 5.00
    assert valor_calculado == 5.26

def test_calcular_multa_com_atraso_longo():
    """
    Testa juros compostos em um período maior (ex: 30 dias).
    """
    dias_atraso = 30
    data_prevista = (date.today() - timedelta(days=dias_atraso)).isoformat()
    
    emprestimo_mock = {
        "Status": "Atrasado",
        "DataDevolucaoPrevista": data_prevista
    }
    
    # Cálculo: 5 * (1.01^30) = 5 * 1.3478... = 6.739... -> 6.74
    valor_calculado = multa.calcular_multa(emprestimo_mock)
    
    assert valor_calculado == 6.74

# --- Testes de Pagamento ---

def test_registrar_pagamento_sucesso():
    """
    Verifica se o pagamento é salvo corretamente na lista.
    """
    id_cliente = 10
    valor_pago = 15.50
    
    sucesso = multa.registrar_pagamento_multa(id_cliente, valor_pago)
    
    assert sucesso is True
    
    # Verifica na lista interna do módulo (ou via getter se existisse)
    # Como estamos testando o módulo isolado, acessamos a lista global recarregada
    assert len(multa._lst_pagamentos) == 1
    pagamento = multa._lst_pagamentos[0]
    
    assert pagamento["ID_Cliente"] == id_cliente
    assert pagamento["Valor"] == valor_pago
    assert pagamento["DataPagamento"] == date.today().isoformat()
    assert pagamento["ID_Pagamento"] == 1 # Primeiro ID

def test_obter_pagamentos_cliente():
    """
    Testa se o filtro por cliente funciona.
    """
    # Registra pagamentos misturados
    multa.registrar_pagamento_multa(1, 5.00) # Cliente 1
    multa.registrar_pagamento_multa(2, 10.00) # Cliente 2
    multa.registrar_pagamento_multa(1, 2.50) # Cliente 1
    
    # Busca só do Cliente 1
    historico_c1 = multa.obter_pagamentos_cliente(1)
    
    assert len(historico_c1) == 2
    assert historico_c1[0]["Valor"] == 5.00
    assert historico_c1[1]["Valor"] == 2.50
    
    # Busca só do Cliente 2
    historico_c2 = multa.obter_pagamentos_cliente(2)
    assert len(historico_c2) == 1