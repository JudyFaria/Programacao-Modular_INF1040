from datetime import date, timedelta
import src.sb.emprestimo as emprestimo
import src.sb.acervo as acervo
import src.sb.gestao_usuarios as gu
import src.sb.multa as multa

# O 'conftest.py' já garante que _remove_data_files() e _reload_sb_modules()
# rodam antes de cada teste via autouse=True. Então começamos com estado limpo.

# --- Testes de Criação de Empréstimo ---

def test_criar_emprestimo_sucesso():
    """
    Testa o fluxo padrão de sucesso (Caminho Feliz).
    """
    # 1. Setup: Cadastrar Livro, Cópia e Cliente
    livro = acervo.cadastrar_livro("Dom Casmurro", "Machado", "Ed. A")
    copias = acervo.add_copias(livro["ID_Livro"], 1, "Corredor A")
    id_copia = copias[0]["ID_Copia"]
    
    cliente = gu.cadastrar_cliente("Ana", "123", "Rua 1", "Tel 1", "senha")
    id_cliente = cliente["ID_Cliente"]

    # 2. Ação: Criar Empréstimo
    novo_emp = emprestimo.criar_emprestimo(id_cliente, id_copia)

    # 3. Verificações
    assert novo_emp is not None
    assert novo_emp["ID_Cliente_Referencia"] == id_cliente
    assert novo_emp["ID_Copia_Referencia"] == id_copia
    assert novo_emp["Status"] == "Em andamento"
    
    # Verifica Data de Devolução (7 dias úteis)
    # Hoje (Assumindo dia útil) + 7 dias úteis deve ser no futuro
    data_inicio = date.fromisoformat(novo_emp["DataInicio"])
    data_fim = date.fromisoformat(novo_emp["DataDevolucaoPrevista"])
    assert data_fim > data_inicio
    
    # Verifica se o status da cópia mudou no Acervo
    copia_no_acervo = acervo._lst_copias_livros[0]
    assert copia_no_acervo["Status"] == "Emprestado"

def test_criar_emprestimo_falha_limite_10():
    """
    Testa se o sistema bloqueia o 11º empréstimo.
    """
    # 1. Setup: Cliente e Livro
    cliente = gu.cadastrar_cliente("Beto", "456", "Rua 2", "Tel 2", "senha")
    livro = acervo.cadastrar_livro("Livro Teste", "Autor", "Ed")
    
    # Adiciona 11 cópias
    copias = acervo.add_copias(livro["ID_Livro"], 11, "Loc")
    
    # 2. Ação: Criar 10 empréstimos (Limite)
    for i in range(10):
        res = emprestimo.criar_emprestimo(cliente["ID_Cliente"], copias[i]["ID_Copia"])
        assert res is not None # Devem funcionar

    # 3. Ação: Tentar o 11º
    res_falha = emprestimo.criar_emprestimo(cliente["ID_Cliente"], copias[10]["ID_Copia"])
    
    # 4. Verificação
    assert res_falha is None # Deve ser bloqueado

def test_criar_emprestimo_falha_copia_indisponivel():
    """
    Testa tentar emprestar uma cópia que já está emprestada.
    """
    livro = acervo.cadastrar_livro("Livro X", "Autor X", "Ed X")
    copias = acervo.add_copias(livro["ID_Livro"], 1, "Loc")
    id_copia = copias[0]["ID_Copia"]
    
    c1 = gu.cadastrar_cliente("C1", "111", "End", "Tel", "Pass")
    c2 = gu.cadastrar_cliente("C2", "222", "End", "Tel", "Pass")

    # C1 pega o livro
    emprestimo.criar_emprestimo(c1["ID_Cliente"], id_copia)

    # C2 tenta pegar A MESMA cópia
    res = emprestimo.criar_emprestimo(c2["ID_Cliente"], id_copia)

    assert res is None # Deve falhar

def test_criar_emprestimo_falha_atraso_pendente():
    """
    Testa o bloqueio se o cliente tiver um empréstimo ATRASADO.
    Este é tricky porque precisamos simular o atraso (viagem no tempo).
    """
    # 1. Setup
    cliente = gu.cadastrar_cliente("Devedor", "999", "Rua", "Tel", "Pass")
    livro = acervo.cadastrar_livro("Livro A", "Autor", "Ed")
    copias = acervo.add_copias(livro["ID_Livro"], 2, "Loc") # 2 cópias
    
    # 2. Cria empréstimo normal
    emp_1 = emprestimo.criar_emprestimo(cliente["ID_Cliente"], copias[0]["ID_Copia"])
    
    # --- SIMULAÇÃO DE ATRASO (HACKING O ESTADO) ---
    # Manualmente alteramos a data de devolução para o PASSADO
    ontem = date.today() - timedelta(days=1)
    emp_1["DataDevolucaoPrevista"] = ontem.isoformat()
    # Forçamos a verificação de atrasos (que normalmente roda no início das funções)
    emprestimo.verificar_e_atualizar_atrasos()
    
    assert emp_1["Status"] == "Atrasado" # Confirma que o sistema detectou

    # 3. Ação: Tentar pegar o segundo livro
    res = emprestimo.criar_emprestimo(cliente["ID_Cliente"], copias[1]["ID_Copia"])

    # 4. Verificação
    assert res is None # Deve ser bloqueado por causa do atraso

# --- Testes de Devolução ---

def test_registrar_devolucao_sucesso():
    """
    Testa o fluxo de devolução.
    """
    # Setup
    livro = acervo.cadastrar_livro("Livro Y", "Autor", "Ed")
    copias = acervo.add_copias(livro["ID_Livro"], 1, "Loc")
    cliente = gu.cadastrar_cliente("Cliente Y", "888", "End", "Tel", "Pass")
    
    emp = emprestimo.criar_emprestimo(cliente["ID_Cliente"], copias[0]["ID_Copia"])
    assert emp["Status"] == "Em andamento"

    # Ação: Devolver
    emp_finalizado = emprestimo.registrar_devolucao(copias[0]["ID_Copia"])

    # Verificações
    assert emp_finalizado["Status"] == "Finalizado"
    assert emp_finalizado["DataDevolucaoReal"] == date.today().isoformat()
    
    # Verifica se a cópia ficou disponível no Acervo
    copia_acervo = acervo._lst_copias_livros[0]
    assert copia_acervo["Status"] == "Disponível"

# --- Testes de Renovação ---

def test_renovar_emprestimo_sucesso():
    """
    Testa renovação normal (sem atraso).
    """
    # Setup
    livro = acervo.cadastrar_livro("Livro Z", "Autor", "Ed")
    copias = acervo.add_copias(livro["ID_Livro"], 1, "Loc")
    cliente = gu.cadastrar_cliente("Renovador", "777", "End", "Tel", "Pass")
    
    emp = emprestimo.criar_emprestimo(cliente["ID_Cliente"], copias[0]["ID_Copia"])
    data_prevista_original = emp["DataDevolucaoPrevista"]

    # Ação: Renovar como Cliente
    sucesso = emprestimo.renovar_emprestimo(emp["ID_Emprestimo"], "Cliente")

    # Verificação
    assert sucesso is True
    assert emp["DataDevolucaoPrevista"] > data_prevista_original


def test_renovacao_funcionario_gera_pagamento_multa():
    """
    Testa o fluxo completo: 
    1. Empréstimo atrasa.
    2. Funcionário solicita renovação.
    3. Sistema DEVE calcular a multa, registrar o pagamento E renovar.
    """
  
    cliente = gu.cadastrar_cliente("Devedor", "999", "Rua", "Tel", "123")
    livro= acervo.cadastrar_livro("Livro Multa", "Autor", "Ed")
    copias = acervo.add_copias(livro["ID_Livro"], 1, "Loc")
    
    # Cria o empréstimo
    emprestimo.criar_emprestimo(cliente["ID_Cliente"], copias[0]["ID_Copia"])
    
    # Recupera o ID do empréstimo
    lista_emps = emprestimo.get_historico_cliente(cliente["ID_Cliente"])
    emp = lista_emps[0]
    emp_id = emp["ID_Emprestimo"]

    # Hack: Simular Atraso de 5 dias
    atraso_dias = 5
    data_passada = date.today() - timedelta(days=atraso_dias)
    
    # Força o estado de atraso na memória
    emp["DataDevolucaoPrevista"] = data_passada.isoformat()
    emp["Status"] = "Atrasado" 

    # Verificação Prévia: Garantir que não há pagamentos antes
    if hasattr(multa, 'obter_pagamentos_cliente'):
        pagamentos_antes = multa.obter_pagamentos_cliente(cliente["ID_Cliente"])
        assert len(pagamentos_antes) == 0
    
    # Calcula quanto deveria ser a multa para comparar depois
    valor_multa_esperado = multa.calcular_multa(atraso_dias)
    assert valor_multa_esperado > 0

    # Funcionário renova
    # Isso deve acionar internamente: Calcular Multa -> Pagar Multa -> Renovar
    sucesso = emprestimo.renovar_emprestimo(emp_id, "Funcionario")

    assert sucesso is True
    assert emp["Status"] == "Em andamento" # Status deve ter voltado ao normal
    assert date.fromisoformat(emp["DataDevolucaoPrevista"]) > date.today() # Data futura

    # Pagamento Registrado
    # Verifica no módulo de multas se o pagamento foi criado
    if hasattr(multa, 'obter_pagamentos_cliente'):
        pagamentos_depois = multa.obter_pagamentos_cliente(cliente["ID_Cliente"])
        assert len(pagamentos_depois) == 1
        assert pagamentos_depois[0]["Valor"] == valor_multa_esperado
        assert pagamentos_depois[0]["DataPagamento"] == date.today().isoformat()
    else:
        # Fallback se não tiver o getter: verifica a lista global
        assert len(multa._lst_pagamentos) == 1
        assert multa._lst_pagamentos[0]["Valor"] == valor_multa_esperado



def test_renovacao_cliente_bloqueada_sem_pagamento():
    """
    Garante que o Cliente NÃO consegue renovar se tiver multa pendente.
    """
    cliente = gu.cadastrar_cliente("Ana", "888", "Rua", "Tel", "123")
    livro = acervo.cadastrar_livro("Livro B", "Aut", "Ed")
    copias = acervo.add_copias(livro["ID_Livro"], 1, "Loc")
    
    emprestimo.criar_emprestimo(cliente["ID_Cliente"], copias[0]["ID_Copia"])
    lista_emps = emprestimo.get_historico_cliente(cliente["ID_Cliente"])
    emp = lista_emps[0]

    # Hack: Simula Atraso
    emp["DataDevolucaoPrevista"] = (date.today() - timedelta(days=5)).isoformat()
    emp["Status"] = "Atrasado"

    # AÇÃO: Tentar renovar como "Cliente"
    sucesso = emprestimo.renovar_emprestimo(emp["ID_Emprestimo"], "Cliente")

    # Verificações
    assert sucesso is False
    
    # Garante que NENHUM pagamento foi gerado
    if hasattr(multa, '_lst_pagamentos'):
        assert len(multa._lst_pagamentos) == 0