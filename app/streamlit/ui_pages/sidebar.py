import streamlit as st


def render_sidebar_login(api):
    '''
        Renderiza o formulário de login.
        Recebe o objeto 'api' (o Façade) como argumento.
    '''

    st.subheader("Login")
    with st.form("sidebar_login_form"):
        username = st.text_input("Usuário (CPF ou Admin)")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            # O backend 'autenticar' não modifica o estado, só lê
            usuario = api.autenticar_usuario(username, password)
            
            if usuario:
                st.session_state.logged_in = True
                st.session_state.usuario_logado = usuario
                
                if usuario['Tipo'] == 'Cliente':
                    st.session_state.selected_page = "Meus Empréstimos"
                else:
                    st.session_state.selected_page = "Gerenciar Acervo"
                
                st.rerun()
            else:
                st.error("Usuário ou senha incorreto!")


def render_sidebar_nav_e_logout(api, todas_as_paginas):
    '''
        Renderiza o menu de navegação e o botão de sair.
        Recebe 'api' e o dicionário 'todas_as_paginas' como argumentos.
    '''
    
    usuario = st.session_state.usuario_logado
    st.write(f"Bem-vindo(a), **{usuario.get('Papel')} {usuario.get('Nome', '_')}**!")
    st.caption(f"Papel: {usuario['Tipo']} ({usuario.get('Papel', 'N/A')})")
    st.divider()

    if usuario['Tipo'] == "Cliente":
        modulos_visiveis = ["Pesquisar Acervo", "Meus Empréstimos"]
    
    elif usuario['Tipo'] == "Funcionario":
        modulos_visiveis = ["Pesquisar Acervo", "Gerenciar Acervo", "Gerenciar Usuários"]
    
    else:
        modulos_visiveis = ["Pesquisar Acervo"]

    opcoes_radio = [nome for nome in todas_as_paginas.keys() if nome in modulos_visiveis]
    
    index_atual = 0
    if st.session_state.selected_page in opcoes_radio:
        index_atual = opcoes_radio.index(st.session_state.selected_page)

    st.session_state.selected_page = st.radio(
        "Módulos", 
        opcoes_radio, 
        key="page_radio",
        index=index_atual
    )
    
    st.divider()
    if st.button("Sair"):
        # Limpa apenas o estado de login da UI
        st.session_state.logged_in = False
        st.session_state.usuario_logado = None
        st.session_state.selected_page = "Pesquisar Acervo"
        st.rerun()