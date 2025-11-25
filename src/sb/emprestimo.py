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
def salvar_alteracoes() -> None:
    """
    Persiste o estado atual dos empréstimos no armazenamento.

    Salva:
        - Lista completa de empréstimos (`_lst_emprestimos`)
        - Próximo ID de empréstimo (`_prox_id_emprestimo`)

    Não recebe parâmetros e não retorna valor.
    """
    persistence.save("emprestimo", {
        "_lst_emprestimos": _lst_emprestimos,
        "_prox_id_emprestimo": _prox_id_emprestimo
    })

def _calcular_data_devolucao(data_inicio: date) -> date:
    """
    Calcula a data de devolução para 7 dias úteis após a data de início.

    Parâmetros:
        data_inicio (date): Data de início do empréstimo.

    Retorna:
        date: Data correspondente a 7 dias úteis após `data_inicio`.
    """

    dias_adicionados = 0
    data_atual = data_inicio
    
    while dias_adicionados < 7:
        data_atual += timedelta(days=1)
        
        if data_atual.weekday() < 5: # 0-4 são dias úteis
            dias_adicionados += 1
    
    return data_atual

def verificar_e_atualizar_atrasos() -> None:
    """
    Verifica todos os empréstimos em andamento e marca como atrasados
    aqueles cuja data de devolução prevista já passou.

    Regras:
        - Apenas empréstimos com Status == "Em andamento" são verificados.
        - Se a data de hoje (`date.today()`) for maior que
          `DataDevolucaoPrevista`, o status é alterado para "Atrasado".
        - Caso ao menos um empréstimo seja alterado, `salvar_alteracoes()`
          é chamada para persistir as mudanças.

    Não recebe parâmetros e não retorna valor.
    """

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

def criar_emprestimo(id_cliente: int, id_copia: int) -> dict | None:
    """
    Cria um novo empréstimo de uma cópia de livro para um cliente.

    Regras de negócio:
        - O cliente pode ter no máximo 10 empréstimos ativos
          (Status "Em andamento" ou "Atrasado").
        - O cliente não pode ter empréstimos atrasados para conseguir
          um novo empréstimo.
        - A cópia do livro deve existir e estar com Status "Disponível".
        - Ao criar o empréstimo:
            * DataInicio = data de hoje (ISO)
            * DataDevolucaoPrevista = 7 dias úteis depois de hoje
            * DataDevolucaoReal = None
            * Status = "Em andamento"
        - A cópia é marcada como "Emprestado" no acervo.

    Parâmetros:
        id_cliente (int): ID do cliente que está realizando o empréstimo.
        id_copia (int): ID da cópia do livro a ser emprestada.

    Retorna:
        dict: Dicionário contendo os dados do novo empréstimo, em caso de sucesso.
        None: Se ocorrer alguma violação das regras (limite, atraso, cópia indisponível, etc.).
    """
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


def registrar_devolucao(id_copia: int) -> dict | None:
    """
    Registra a devolução de uma cópia de livro.

    Parâmetros:
        id_copia (int): ID da cópia devolvida.

    Retorna:
        dict: Dicionário do empréstimo atualizado, em caso de sucesso.
        None: Se não houver empréstimo ativo associado à cópia.
    """
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

def renovar_emprestimo(id_emprestimo: int, tipo_usuario: str) -> bool:
    """
    Renova um empréstimo, estendendo a data de devolução prevista em 7 dias úteis.

    Regras:
        - Empréstimos finalizados não podem ser renovados.
        - Se o empréstimo estiver "Em andamento":
            * Apenas calcula uma nova DataDevolucaoPrevista (7 dias úteis após
              a data prevista atual).
        - Se o empréstimo estiver "Atrasado":
            * Tipo "Cliente":
                - Não pode renovar; deve se dirigir ao balcão.
            * Tipo "Funcionario":
                - Pode renovar, mas:
                    1. É calculada uma multa via `multa.calcular_multa(emprestimo)`.
                    2. O pagamento é registrado via
                       `multa.registrar_pagamento_multa(...)`.
                    3. Se o pagamento não for concluído, a renovação não ocorre.
                    4. Se o pagamento for concluído, a renovação prossegue.

    Parâmetros:
        id_emprestimo (int): ID do empréstimo a ser renovado.
        tipo_usuario (str): "Cliente" ou "Funcionario", usado para
            aplicar as regras de atraso.

    Retorna:
        bool:
            - True se a renovação foi realizada com sucesso.
            - False em caso de erro, empréstimo não encontrado, finalizado,
              atraso sem permissão ou falha no pagamento da multa.
    """
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

def get_historico_cliente(id_cliente: int) -> list[dict]:
    """
    Obtém todo o histórico de empréstimos de um cliente.

    Parâmetros:
        id_cliente (int): ID do cliente cujo histórico será consultado.

    Retorna:
        list[dict]: Lista de todos os empréstimos associados ao cliente.
    """
    historico = []
    for emp in _lst_emprestimos:
        if emp["ID_Cliente_Referencia"] == id_cliente:
            historico.append(emp)
    return historico