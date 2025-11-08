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

_lst_livros = []
_lst_copias_livros = []

_prox_id_livro = 1
_prox_id_copia = 1

def cadastrar_livro(titulo, autor, edicao):

    '''
        Verifica se um LIVRO (título/autor/edição) já existe.
        Se não existir, cadastra na _lst_livros.
        Retorna o dicionário do livro (novo ou o que já existia).
    '''

    global _prox_id_livro
    livro_existente = None

    for livro in _lst_livros:

        if ( (livro["Titulo"] == titulo) and (livro["Autor"] ==  autor) and (livro["Edicao"] == edicao)):
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
    
        return novo_livro


def add_copias(id_livro_ref, localiazacao):
    
    '''
        Adiciona cópia de um livro existente na lista de livros
    '''

    global _prox_id_copia

    livro_existe = False

    for livro in _lst_livros:

        if (livro["ID_Livro"] == id_livro_ref):
            livro_existe = True
            break

    if not livro_existe:
        print(f"Erro: Não é possível adicionar cópia. O Livro com id {id_livro_ref} não existe.")
        return None
        
    else:

        nova_copia = {
            "ID_Copia": _prox_id_copia,
            "ID_Livro_Referencia": id_livro_ref,
            "LocalizacaoFisica": localiazacao,
            "Status": "Disponível" 
        }

        _lst_copias_livros.append(nova_copia)
        _prox_id_copia += 1

        return nova_copia



def buscar_livro(termo_busca):

    '''
        Busca o livro por Título, Autor ou Edição (editora)
        Retorna uma lista das cópias do livro pesquisado e suas respectivas disponibilidades
    '''
    global _lst_livros
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
            if copia["Status"] == "Emprestada":
                copia_emprestada = copia
                break

    if copia_emprestada:
        print(f"ERRO: Exclusão falhou.")
        print(f"O livro (ID: {id_livro}) não pode ser excluído pois a")
        print(f"cópia (ID: {copia_emprestada['ID_Copia']}) está 'Emprestado'.")
        return False 

    # Exclusão (de forma segura)
    
    # copias
    copias_manter = []
    for copia in _lst_copias_livros:
        if (copia["ID_Livro_Referencia"] != id_livro):
            copias_manter.append(copia)
    
    qtd_copias_removidas =  len(_lst_copias_livros) - len(copias_manter) # mensagem 
    _lst_copias_livros = copias_manter

    # título (livro)
    titulos_manter = []
    livro_excluido = None
    
    for livro in _lst_livros:
        if (livro["ID_Livro"] != id_livro):
            titulos_manter.append(livro)

        else:
            livro_excluido = livro["Titulo"] # mensagem
    
    _lst_livros = titulos_manter

    if livro_excluido:
        print(f"SUCESSO: Livro '{livro_excluido}' (ID: {id_livro})")
        print(f"e suas {qtd_copias_removidas} cópias foram excluídos.")
    else:
        # Caso do ID inexistente
        print(f"INFO: Nenhum livro encontrado com o ID {id_livro}.")
    
    return True
