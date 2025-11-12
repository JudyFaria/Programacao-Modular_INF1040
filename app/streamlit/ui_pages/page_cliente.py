import streamlit as st

def render_page_meus_emprestimos(api):
    '''
        Renderiza a página de empréstimos do cliente.
        Recebe o objeto 'api' (o Façade) como argumento.
    '''
    st.title("Meus Empréstimos")
    nome_cliente = st.session_state.usuario_logado['nome_usuario']
    st.write(f"Olá, **{nome_cliente}**. Aqui está seu histórico:")
    
    st.info("MÓDULO EM CONSTRUÇÃO")
    
    # Lógica futura:
    # id_cliente = st.session_state.usuario_logado['id']
    # meus_emprestimos = api.consultar_historico_cliente(id_cliente)
    # st.dataframe(meus_emprestimos)