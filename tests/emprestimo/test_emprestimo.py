import pytest
from datetime import date, timedelta
import src.sb.emprestimo as emprestimo


def test_calcular_data_devolucao_pula_fins_de_semana():
    # Começa numa segunda-feira conhecida
    inicio = date(2025, 11, 3)  # Monday
    resultado = emprestimo._calcular_data_devolucao(inicio)
    # 7 dias úteis depois de 03/11/2025 é 14/11/2025 (contando 7 weekdays)
    assert resultado.weekday() < 5
    assert (resultado - inicio).days >= 9  # must skip weekend days


def test_criar_emprestimo_sucesso_altera_copia_e_contador():
    db_emp = []
    db_copias = [{"ID_Copia": 1, "ID_Livro_Referencia": 1, "Status": "Disponível"}]
    prox = 1

    db_emp, db_copias, prox, sucesso, msg = emprestimo.criar_emprestimo(1, 1, db_emp, db_copias, prox)

    assert sucesso is True
    assert len(db_emp) == 1
    assert db_emp[0]["ID_Emprestimo"] == 1
    assert db_copias[0]["Status"] == "Emprestado"
    assert prox == 2


def test_criar_emprestimo_copia_nao_encontrada_falha():
    db_emp = []
    db_copias = []
    prox = 1

    db_emp, db_copias, prox, sucesso, msg = emprestimo.criar_emprestimo(1, 99, db_emp, db_copias, prox)

    assert sucesso is False
    assert "Cópia não encontrada" in msg


def test_criar_emprestimo_copia_indisponivel_falha():
    db_emp = []
    db_copias = [{"ID_Copia": 1, "Status": "Emprestado"}]
    prox = 1

    db_emp, db_copias, prox, sucesso, msg = emprestimo.criar_emprestimo(1, 1, db_emp, db_copias, prox)

    assert sucesso is False
    assert "não está disponível" in msg


def test_criar_emprestimo_limite_dez_falha():
    # cria 10 empréstimos ativos para o cliente 1
    db_emp = []
    for i in range(10):
        db_emp.append({"ID_Emprestimo": i + 1, "ID_Cliente_Referencia": 1, "Status": "Em andamento", "ID_Copia_Referencia": 100 + i, "DataDevolucaoPrevista": date.today() + timedelta(days=10), "DataInicio": date.today(), "DataDevolucaoReal": None})
    db_copias = [{"ID_Copia": 200, "Status": "Disponível"}]
    prox = 1000

    db_emp, db_copias, prox, sucesso, msg = emprestimo.criar_emprestimo(1, 200, db_emp, db_copias, prox)

    assert sucesso is False
    assert "limite de 10 empréstimos" in msg


def test_criar_emprestimo_com_pendencia_atrasada_falha():
    db_emp = [{"ID_Emprestimo": 1, "ID_Cliente_Referencia": 1, "Status": "Atrasado", "ID_Copia_Referencia": 5, "DataDevolucaoPrevista": date.today() - timedelta(days=5), "DataInicio": date.today() - timedelta(days=12), "DataDevolucaoReal": None}]
    db_copias = [{"ID_Copia": 2, "Status": "Disponível"}]
    prox = 2

    db_emp, db_copias, prox, sucesso, msg = emprestimo.criar_emprestimo(1, 2, db_emp, db_copias, prox)

    assert sucesso is False
    assert "ATRASADOS" in msg or "ATRASADO" in msg


def test_verificar_atrasos_marca_como_atrasado():
    passado = date.today() - timedelta(days=10)
    db_emp = [{"ID_Emprestimo": 1, "ID_Cliente_Referencia": 1, "Status": "Em andamento", "DataDevolucaoPrevista": passado, "ID_Copia_Referencia": 1, "DataInicio": passado - timedelta(days=7), "DataDevolucaoReal": None}]

    resultado = emprestimo.verificar_atrasos(db_emp)

    assert resultado[0]["Status"] == "Atrasado"


def test_registrar_devolucao_sucesso_e_libera_copia():
    db_emp = [{"ID_Emprestimo": 1, "ID_Copia_Referencia": 10, "ID_Cliente_Referencia": 1, "Status": "Em andamento", "DataDevolucaoPrevista": date.today() + timedelta(days=1), "DataInicio": date.today(), "DataDevolucaoReal": None}]
    db_copias = [{"ID_Copia": 10, "Status": "Emprestado"}]

    db_emp, db_copias, sucesso, msg = emprestimo.registrar_devolucao(10, db_emp, db_copias)

    assert sucesso is True
    assert db_emp[0]["Status"] == "Finalizado"
    assert db_copias[0]["Status"] == "Disponível"


def test_registrar_devolucao_sem_emprestimo_ativo_falha():
    db_emp = []
    db_copias = [{"ID_Copia": 11, "Status": "Disponível"}]

    db_emp, db_copias, sucesso, msg = emprestimo.registrar_devolucao(11, db_emp, db_copias)

    assert sucesso is False
    assert "Não há empréstimo ativo" in msg


def test_renovar_emprestimo_cliente_nao_permite_se_atrasado():
    db_emp = [{"ID_Emprestimo": 1, "ID_Cliente_Referencia": 1, "Status": "Atrasado", "DataDevolucaoPrevista": date.today() - timedelta(days=1)}]

    db_emp, sucesso, msg = emprestimo.renovar_emprestimo(1, "Cliente", db_emp)

    assert sucesso is False
    assert "não é possível renovar" in msg or "Não é possível renovar" in msg


def test_renovar_emprestimo_funcionario_renova_atrasado():
    previsao = date.today() - timedelta(days=2)
    db_emp = [{"ID_Emprestimo": 2, "ID_Cliente_Referencia": 2, "Status": "Atrasado", "DataDevolucaoPrevista": previsao}]

    db_emp, sucesso, msg = emprestimo.renovar_emprestimo(2, "Funcionario", db_emp)

    assert sucesso is True
    # status deve ter sido resetado para 'Em andamento' quando renovado por funcionário
    assert any(e["ID_Emprestimo"] == 2 and e["Status"] == "Em andamento" for e in db_emp)


def test_get_todos_emprestimos_retorna_lista_global():
    # modifica a lista global diretamente e verifica retorno
    emprestimo._lst_emprestimos.clear()
    emprestimo._lst_emprestimos.append({"ID_Emprestimo": 99})

    todos = emprestimo.get_todos_emprestimos()
    assert isinstance(todos, list)
    assert todos[0]["ID_Emprestimo"] == 99
