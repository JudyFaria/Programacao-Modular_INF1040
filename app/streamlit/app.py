import streamlit as st
from src.sb.api import api_facade
from ui_pages import page_cliente, page_funcionario, page_public, sidebar

@st.cache_resource #protege de ser reiniciado
def get_api_facade():
    '''
        Esta função é executada APENAS UMA VEZ por sessão
        Importa o backend e "guarda" na memóris
        O Streamlit NUNCA a executará novamente
    '''

    api_facade.inicializar_sistema()
    
    return api_facade


def main():
    st.set_page_config(page_title="Sistema de Biblioteca", layout="wide")
    
    api = get_api_facade()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.usuario_logado = None
        st.session_state.selected_page = "Pesquisar Acervo"

    # Define o mapa de quais páginas existem
    pages = {
        # Páginas Públicas
        "Pesquisar Acervo": page_public.render_page_pesquisar,
       
        # Páginas de Cliente
        "Meus Empréstimos": page_cliente.render_page_meus_emprestimos,
        
        # Páginas de Funcionário
        "Gerenciar Acervo": page_funcionario.render_page_gerenciar_acervo,
        "Gerenciar Usuários": page_funcionario.render_page_gerenciar_usuarios,
        # "Gerenciar Empréstimos": page_funcionario.render_page_gerenciar_emprestimos, (futuro)
        # "Relatórios": page_funcionario.render_page_relatorios, (futuro)
    }
    
    # Sidebar
    with st.sidebar:
        st.title("Biblioteca")
        
        if not st.session_state.logged_in:
            sidebar.render_sidebar_login(api)
            st.session_state.selected_page = "Pesquisar Acervo"
        else:
            sidebar.render_sidebar_nav_e_logout(api, pages)

    # Conteúdo Principal da Página
    page_name = st.session_state.get('selected_page', "Pesquisar Acervo")
    page_function = pages.get(page_name)
    
    if page_function:
        page_function(api)
    else:
        st.error("Página não encontrada.")


# --- Ponto de Entrada Padrão do Python ---
if __name__ == "__main__":
    main()