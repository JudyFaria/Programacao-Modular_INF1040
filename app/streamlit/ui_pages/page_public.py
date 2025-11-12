import streamlit as st

import streamlit as st

def render_page_pesquisar(api):
    '''
        Renderiza a página pública de pesquisa.
        Recebe o objeto 'api' (o Façade) como argumento.
    '''
    st.title("Pesquisar Acervo")
    termo = st.text_input("Digite o termo da busca:")
    
    if termo:
        # Chama a API (Façade)
        resultados = api.buscar_livro(termo) 
        
        if not resultados:
            st.warning("Nenhum livro encontrado.")
        else:
            st.success(f"{len(resultados)} livro(s) encontrado(s):")
            for item in resultados:
                st.subheader(f"{item['Livro']['Titulo']} (ID: {item['Livro']['ID_Livro']})")
                st.caption(f"Autor: {item['Livro']['Autor']} | Edição: {item['Livro']['Edicao']}")
                if not item["Copias"]:
                    st.info("Este título está cadastrado, mas não há cópias disponíveis.")
                else:
                    st.table([{"ID": c["ID_Copia"], "Status": c["Status"], "Local": c["LocalizacaoFisica"]} for c in item["Copias"]])
                st.divider()