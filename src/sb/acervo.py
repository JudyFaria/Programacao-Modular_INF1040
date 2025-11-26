# NÃO PODE CRIAR CLASSES

# Livro (Título):
#     ID_Livro (Inteiro, Chave Primária)
#     Titulo (Texto)
#     Autor (Texto)
#     Editora (Texto)

# Copia (Exemplar Físico):
#     ID_Copia (Inteiro, Chave Primária)
#     ID_Livro_Referencia (Chave Estrangeira para Livro)
#     LocalizacaoFisica (Texto)
#     Status (Texto: "Disponível", "Emprestado")

from src.sb import emprestimo as ge
from src.sb import persistence

# Load persisted state (if any)
_loaded_state = persistence.load("acervo", {})

_lst_livros = _loaded_state.get("_lst_livros", [])
_lst_copias_livros = _loaded_state.get("_lst_copias_livros", [])
_prox_id_livro = _loaded_state.get("_prox_id_livro", 1)
_prox_id_copia = _loaded_state.get("_prox_id_copia", 1)

def salvar_estado_acervo() -> None:
    """
    Persiste o estado atual do acervo no arquivo JSON.
    Deve ser chamada apenas no encerramento da aplicação.
    """
    persistence.save("acervo", {
        "_lst_livros": _lst_livros,
        "_lst_copias_livros": _lst_copias_livros,
        "_prox_id_livro": _prox_id_livro,
        "_prox_id_copia": _prox_id_copia,
    })

def cadastrar_livro(titulo: str, autor: str, editora: str) -> dict:
    """
    Verifica se um LIVRO (título/autor/editora) já existe.
        Se não existir, cadastra em `_lst_livros`.

    Parâmetros:
        titulo (str): Título do livro.
        autor  (str): Nome do autor.
        editora (str): Nome da editora.

    Retorno:
        dict:
            Dicionário do livro correspondente:
                - Se já existir, retorna o livro existente.
                - Caso contrário, retorna o novo livro cadastrado.
    """

    global _prox_id_livro, _lst_livros
    livro_existente = None

    for livro in _lst_livros:

        if ( (livro["Titulo"] == titulo) 
            and (livro["Autor"] ==  autor) 
            and (livro["Editora"] == editora)
        ):
            livro_existente = livro
            break # não procura mais 

    if livro_existente:
        # print(f"Erro! O livro '{titulo}'  (Editora {editora}) já está cadastrado com o Id {livro["ID_livro"]}.")
        return livro_existente
    
    else: 
        novo_livro = {
            "ID_Livro": _prox_id_livro,
            "Titulo": titulo,
            "Autor": autor,
            "Editora": editora
        }

        _lst_livros.append(novo_livro)
        _prox_id_livro += 1
        
        return novo_livro


def add_copias(id_livro_ref: int, qtd_copias: int, localizacao: str) -> list[dict] | None:
    """
    Adiciona uma ou mais cópias de um livro já existente na lista de livros.

    Parâmetros:
        id_livro_ref (int):
            ID do livro ao qual as cópias estarão vinculadas.
        qtd_copias (int):
            Quantidade de cópias a serem criadas.
        localizacao (str):
            Localização física das cópias (ex.: "Estante A, Prateleira 3").

    Retorno:
        list[dict] | None:
            - Lista de dicionários das cópias criadas, em caso de sucesso.
            - None, se o livro de referência não existir.
    """

    global _prox_id_copia, _lst_copias_livros

    livro_existe = False
    copias_add = []

    for livro in _lst_livros:

        if (livro["ID_Livro"] == id_livro_ref):
            livro_existe = True
            break

    if not livro_existe:
        print(f"Erro: Não é possível adicionar cópia. O Livro com id {id_livro_ref} não está cadastrado no sistema.")
        return None
        

    for i in range(qtd_copias):

        nova_copia = {
            "ID_Copia": _prox_id_copia,
            "ID_Livro_Referencia": id_livro_ref,
            "LocalizacaoFisica": localizacao,
            "Status": "Disponível" 
        }

        _lst_copias_livros.append(nova_copia)
        copias_add.append(nova_copia)
        _prox_id_copia += 1

    return copias_add



def buscar_livro(termo_busca: str) -> list[dict]:
    """
    Busca livros por Título, Autor ou Editora.

    A busca é feita de forma case-insensitive, verificando se o termo
    aparece em qualquer um dos campos.

    Parâmetros:
        termo_busca (str):
            Palavra ou trecho a ser buscado em:
                - Titulo
                - Autor
                - Editora

    Retorno:
        list[dict]:
            Lista de dicionários, onde cada elemento possui a forma:
                {
                    "Livro": <dict com dados do livro>,
                    "Copias": <lista de cópias (dicts) daquele livro>
                }
            Se nenhum livro for encontrado, retorna lista vazia.
    """
    resultado_busca = []

    # encontrar os ids dos livros
    for livro in _lst_livros:

        if ( (termo_busca.lower() in livro["Titulo"].lower() ) 
            or ( termo_busca.lower() in livro["Autor"].lower() )
            or ( termo_busca.lower() in livro["Editora"].lower()) 
            ):
            
            id_livro_achado = livro["ID_Livro"]
            copias_deste_livro = []

            for copia in _lst_copias_livros:
                if copia["ID_Livro_Referencia"] == id_livro_achado:
                    copias_deste_livro.append(copia)

            #montando dicionário do resultado
            resultado_este_livro = {
                "Livro": livro,
                "Copias": copias_deste_livro,
            }

            resultado_busca.append(resultado_este_livro)

    return resultado_busca


def excluir_livro_e_copias(id_livro: int) -> bool:
    """
    Remove um título e todas as suas cópias.

    Regra:
        - Só permite a exclusão se nenhuma cópia do livro estiver
            emprestada (Status "Emprestado" ou empréstimo não finalizado).

    Parâmetros:
        id_livro (int):
            ID do livro a ser excluído.

    Retorno:
        bool:
            - True se o livro e suas cópias forem excluídos com sucesso.
            - False se houver cópias emprestadas ou se o ID for inexistente.
    """
    global _lst_copias_livros, _lst_livros
    copia_emprestada = None
    
    # Verificação se há cópias em empréstimo
    for copia in _lst_copias_livros:
        
        if ( copia["ID_Livro_Referencia"] != id_livro ):
            continue

        # Se o status da cópia já indica 'Emprestado', bloqueia direto
        if copia.get("Status") == "Emprestado":
            copia_emprestada = copia
            break
        
        # Pergunta AO MÓDULO DE EMPRÉSTIMO se há empréstimo ativo
        if ge.copia_possui_emprestimo_ativo(copia["ID_Copia"]):
            copia_emprestada = copia
            break

    if copia_emprestada:
        print(f"ERRO: Exclusão falhou - Exemplar possui empréstimo ativo.")
        print(f"O livro (ID: {id_livro}) não pode ser excluído pois a")
        print(f"cópia (ID: {copia_emprestada['ID_Copia']}) está 'Emprestado'.")
        return False 

    # Exclusão (de forma segura)
    copias_manter = [c for c in _lst_copias_livros if c["ID_Livro_Referencia"] != id_livro]
    livros_manter = [l for l in _lst_livros if l["ID_Livro"] != id_livro]

    if len(livros_manter) == len(_lst_livros):
        # Caso do ID inexistente
        print(f"INFO: Nenhum livro encontrado com o ID {id_livro}.")
        return False
    
    _lst_copias_livros = copias_manter
    _lst_livros = livros_manter

    print(f"SUCESSO: Livro (ID: {id_livro}) e suas cópias foram excluídos.")
    return True

def get_todos_livros():
    """
    Função auxiliar para o front-end.

    Retorna:
        list[dict]:
            Lista com todos os livros cadastrados no acervo.
    """
    return _lst_livros

def get_todas_copias():
    """
    Função auxiliar para o front-end.

    Retorna:
        list[dict]:
            Lista com todas as cópias cadastradas no acervo.
    """
    return _lst_copias_livros

def get_copia_por_id(id_copia: int) -> dict | None:
    """
    Busca e retorna uma cópia específica pelo ID.

    Parâmetros:
        id_copia (int): ID da cópia desejada.

    Retorno:
        dict | None:
            - Dicionário da cópia, se encontrada.
            - None se não existir cópia com esse ID.
    """
    for copia in _lst_copias_livros:
        if copia["ID_Copia"] == id_copia:
            return copia
    return None


def atualizar_status_copia(id_copia: int, novo_status: str) -> bool:
    """
    Atualiza o campo 'Status' de uma cópia específica.

    Parâmetros:
        id_copia (int): ID da cópia que terá o status alterado.
        novo_status (str): Novo status (ex: 'Disponível', 'Emprestado').

    Retorno:
        bool:
            - True se a cópia foi encontrada e atualizada.
            - False se a cópia não existir.
    """
    copia = get_copia_por_id(id_copia)
    if copia is None:
        return False

    copia["Status"] = novo_status
    return True