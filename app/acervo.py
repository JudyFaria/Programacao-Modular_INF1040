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

_prox_id_livro = 1
_prox_id_copia =1

def cadastrar_livro(titulo, autor, edicao):

    '''
        Percorrer a lista de livros
        se o livro a ser adicionado não estiver, adiciona
        se estiver na lista, retorna que não é possível adicionar, pois já existe
    '''

    

    for i, livro in enumerate(_lst_livros):

        if ( livro["ID_Livro"] == )

        novo_livro = {
            "ID_Livro": _prox_id_livro,
            "Titulo": titulo,
            "Autor": autor,
            "Edicao": edicao
        }


