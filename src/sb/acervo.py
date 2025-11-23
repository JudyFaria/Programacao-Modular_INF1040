# NÃO PODE CRIAR CLASSES

# Livro (Título):
#     ID_Livro (Inteiro, Chave Primária)
#     Titulo (Texto)
#     Autor (Texto)
#     Edicao (Texto)

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

def cadastrar_livro(titulo, autor, edicao):

    '''
        Verifica se um LIVRO (título/autor/edição) já existe.
        Se não existir, cadastra na _lst_livros.
        Retorna o dicionário do livro (novo ou o que já existia).
    '''

    global _prox_id_livro, _lst_livros
    livro_existente = None

    for livro in _lst_livros:

        if ( (livro["Titulo"] == titulo) 
            and (livro["Autor"] ==  autor) 
            and (livro["Edicao"] == edicao)
        ):
            livro_existente = livro
            break # não procura mais 

    if livro_existente:
        # print(f"Erro! O livro '{titulo}'  (Ed. {edicao}) já está cadastrado com o Id {livro["ID_livro"]}.")
        return livro_existente
    
    else: 
        novo_livro = {
            "ID_Livro": _prox_id_livro,
            "Titulo": titulo,
            "Autor": autor,
            "Edicao": edicao
        }

        _lst_livros.append(novo_livro)
        _prox_id_livro += 1
        # persist changes
        persistence.save("acervo", {
            "_lst_livros": _lst_livros,
            "_lst_copias_livros": _lst_copias_livros,
            "_prox_id_livro": _prox_id_livro,
            "_prox_id_copia": _prox_id_copia,
        })
    
        return novo_livro


def add_copias(id_livro_ref, qtd_copias, localiazacao):
    
    '''
        Adiciona cópia de um livro existente na lista de livros
    '''

    global _prox_id_copia, _lst_copias_livros

    livro_existe = False
    copias_add = []

    for livro in _lst_livros:

        if (livro["ID_Livro"] == id_livro_ref):
            livro_existe = True
            break

    if not livro_existe:
        print(f"Erro: Não é possível adicionar cópia. O Livro com id {id_livro_ref} não existe.")
        return None
        

    for i in range(qtd_copias):

        nova_copia = {
            "ID_Copia": _prox_id_copia,
            "ID_Livro_Referencia": id_livro_ref,
            "LocalizacaoFisica": localiazacao,
            "Status": "Disponível" 
        }

        _lst_copias_livros.append(nova_copia)
        copias_add.append(nova_copia)
        _prox_id_copia += 1

    # persist changes
    persistence.save("acervo", {
        "_lst_livros": _lst_livros,
        "_lst_copias_livros": _lst_copias_livros,
        "_prox_id_livro": _prox_id_livro,
        "_prox_id_copia": _prox_id_copia,
    })

    return copias_add



def buscar_livro(termo_busca):

    '''
        Busca o livro por Título, Autor ou Edição (editora)
        Retorna uma lista das cópias do livro pesquisado e suas respectivas disponibilidades
    '''
    resultado_busca = []

    # encontrar os ids dos livros
    for livro in _lst_livros:

        if ( (termo_busca.lower() in livro["Titulo"].lower() ) 
            or ( termo_busca.lower() in livro["Autor"].lower() )
            or ( termo_busca.lower() in livro["Edicao"].lower()) 
            ):
            
            id_livro_achado = livro["ID_Livro"]
            copias_deste_livro = []

            for copia in _lst_copias_livros:
                if copia["ID_Livro_Referencia"] == id_livro_achado:
                    copias_deste_livro.append(copia)

            #montando dicionário do resutado
            resultado_este_livro = {
                "Livro": livro,
                "Copias": copias_deste_livro,
            }

            resultado_busca.append(resultado_este_livro)

    return resultado_busca


def excluir_livro_e_copias(id_livro):

    '''
        Remove um título e todas as suas cópias
        Se, e somente se, não houver cópias em empréstimo
    '''
    global _lst_copias_livros, _lst_livros
    copia_emprestada = None
    
    # Verificação se há cópias em empréstimo
    for copia in _lst_copias_livros:
        
        if ( copia["ID_Livro_Referencia"] == id_livro ):

            # se o status da cópia já indica 'Emprestado', basta bloquear
            if copia.get("Status") == "Emprestado":
                copia_emprestada = copia
                break
         
            for emprestimo in ge._lst_emprestimos:
                if ( (emprestimo.get("ID_Copia_Referencia") == copia["ID_Copia"]) 
                    and (emprestimo.get("Status") != "Finalizado")
                ):
                    copia_emprestada = copia
                    break

            if (copia_emprestada):
                break

    if copia_emprestada:
        print(f"ERRO: Exclusão falhou.")
        print(f"O livro (ID: {id_livro}) não pode ser excluído pois a")
        print(f"cópia (ID: {copia_emprestada['ID_Copia']}) está 'Emprestado'.")
        return False 

    # Exclusão (de forma segura)
    
    # copias
    copias_manter = [c for c in _lst_copias_livros if c["ID_Livro_Referencia"] != id_livro]
    livros_manter = [l for l in _lst_livros if l["ID_Livro"] != id_livro]

    if len(livros_manter) == len(_lst_livros):
        # Caso do ID inexistente
        print(f"INFO: Nenhum livro encontrado com o ID {id_livro}.")
        return False
    
    _lst_copias_livros = copias_manter
    _lst_livros = livros_manter

    print(f"SUCESSO: Livro (ID: {id_livro}) e suas cópias foram excluídos.")
   
    # persist changes
    persistence.save("acervo", {
        "_lst_livros": _lst_livros,
        "_lst_copias_livros": _lst_copias_livros,
        "_prox_id_livro": _prox_id_livro,
        "_prox_id_copia": _prox_id_copia,
    })

    return True

def get_todos_livros():
    '''
        Função auxiiar para o front end
    '''
    return _lst_livros