from datetime import date
from src.sb import persistence
from src.sb import emprestimo as ge

# --- Configurações da Multa ---
VALOR_BASE_MULTA = 5.00  # Valor fixo inicial ao atrasar (R$)
TAXA_DIARIA = 0.01       # Taxa de 1% ao dia (Juros Compostos)

# --- Carrega estado persistido ---
_loaded_state = persistence.load("multas", {})

_lst_pagamentos = _loaded_state.get("_lst_pagamentos", [])
_prox_id_pagamento = _loaded_state.get("_prox_id_pagamento", 1)


def salvar_estado_multas() -> None:
    """
    Persiste o estado atual das multas no arquivo JSON.
    Deve ser chamada apenas no encerramento da aplicação.
    """
    persistence.save("multas", {
        "_lst_pagamentos": _lst_pagamentos,
        "_prox_id_pagamento": _prox_id_pagamento
    })


# --- Funções Principais ---

def calcular_multa(dias_atraso: int) -> float:
    """
    Calcula o valor da multa usando Juros Compostos (RF-024).

        Fórmula:
            M = P * (1 + i)^t
            Onde:
            P = Valor Base
            i = Taxa Diária
            t = Dias de Atraso

        Parâmetros:
            dias_atraso (int):
                Número de dias em atraso.

        Retorno:
            float:
                Valor da multa arredondado para 2 casas decimais.
                Retorna 0.0 se o empréstimo não estiver atrasado.
    """
    if dias_atraso <= 0:
        return 0.0
    
    # Cálculo de Juros Compostos
    montante = VALOR_BASE_MULTA * ((1 + TAXA_DIARIA) ** dias_atraso)
    
    # Arredonda para 2 casas decimais
    return round(montante, 2)


def registrar_pagamento_multa(id_cliente: int, valor: float) -> bool:
    """
    Registra um pagamento de multa pelo cliente (RF-026).

    Parâmetros:
        id_cliente (int):
            ID do cliente pagador.
        valor (float):
            Valor da multa a ser paga.

    Retorno:
        bool:
            True se o pagamento for registrado com sucesso.
    """
    global _prox_id_pagamento
    
    novo_pagamento = {
        "ID_Pagamento": _prox_id_pagamento,
        "ID_Cliente": id_cliente,
        "Valor": valor,
        "DataPagamento": date.today().isoformat()
    }
    
    _lst_pagamentos.append(novo_pagamento)
    _prox_id_pagamento += 1
    
    print(f"Pagamento de multa registrado: R$ {valor:.2f} (Cliente ID: {id_cliente})")
    return True

def obter_pagamentos_cliente(id_cliente: int) -> list[dict]:
    """
    Retorna o histórico de pagamentos de multa de um cliente.

    Parâmetros:
        id_cliente (int):
            Identificador do cliente.

    Retorno:
        list[dict]:
            Lista contendo todos os pagamentos já feitos pelo cliente.
    """
    return [p for p in _lst_pagamentos if p["ID_Cliente"] == id_cliente]