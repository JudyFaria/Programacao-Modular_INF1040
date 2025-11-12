import streamlit as st

def render_page_gerenciar_acervo(api):
    '''
        Renderiza a página de gestão de acervo.
        Recebe o objeto 'api' (o Façade) como argumento.
    '''
    st.title("Gerenciar Acervo (Livros e Cópias)")
    tab1, tab2, tab3 = st.tabs(["Cadastrar Novo Título", "Adicionar Cópias", "Excluir Livro"])

    with tab1:
        st.subheader("Cadastrar Novo Título e Cópias Iniciais")
        with st.form("novo_livro_form", clear_on_submit=True):
            titulo = st.text_input("Título")
            autor = st.text_input("Autor")
            edicao = st.text_input("Edição/Editora")
            st.divider()
            quantidade = st.number_input("Qtd. Cópias", min_value=1, value=1)
            localizacao = st.text_input("Localização")
            
            if st.form_submit_button("Cadastrar Título e Cópias"):
                livro, status_livro = api.cadastrar_livro(titulo, autor, edicao) # Chama a API
                if "Erro" in status_livro:
                    st.error(f"Erro ao cadastrar livro: {status_livro}")
                else:
                    status_copia = api.add_copias(livro["ID_Livro"], quantidade, localizacao) # Chama a API
                    if status_copia == "sucesso":
                        st.success(f"Livro '{livro['Titulo']}' e {quantidade} cópia(s) cadastrados!")
                    else:
                        st.error("Erro ao adicionar cópias.")

    with tab2:
        st.subheader("Adicionar Cópias a um Título Existente")
        livros = api.get_todos_livros() # Chama a API
        if not livros:
            st.warning("Nenhum livro cadastrado.")
        else:
            opcoes = {f"ID {l['ID_Livro']}: {l['Titulo']}": l['ID_Livro'] for l in livros}
            selecionado = st.selectbox("Selecione o livro", ["Selecione..."] + list(opcoes.keys()))
            if selecionado != "Selecione...":
                id_livro = opcoes[selecionado]
                with st.form("add_copias_form", clear_on_submit=True):
                    qtd = st.number_input("Qtd. Novas Cópias", min_value=1, value=1)
                    loc = st.text_input("Localização")
                    if st.form_submit_button("Adicionar Cópias"):
                        _, status = api.add_copias(id_livro, qtd, loc) # Chama a API
                        if status == "sucesso": 
                            st.success("Cópias adicionadas!")
                        else: 
                            st.error("Erro ao adicionar cópias.")

    with tab3:
        st.subheader("Excluir um Título (e todas as suas cópias)")
        livros = api.get_todos_livros() # Chama a API
        if not livros:
            st.warning("Nenhum livro para excluir.")
        else:
            opcoes_excluir = {f"ID {l['ID_Livro']}: {l['Titulo']}": l['ID_Livro'] for l in livros}
            selecionado_excluir = st.selectbox("Selecione o livro a excluir", ["Selecione..."] + list(opcoes_excluir.keys()))
            if selecionado_excluir != "Selecione...":
                id_excluir = opcoes_excluir[selecionado_excluir]
                if st.button(f"Confirmar Exclusão de '{selecionado_excluir}'", type="primary"):
                    sucesso, msg = api.excluir_livro(id_excluir) # Chama a API
                    if sucesso: 
                        st.success(msg)
                        st.rerun() # Atualiza a UI para remover o livro da lista
                    else: 
                        st.error(msg)


def render_page_gerenciar_usuarios(api):
    '''
        Renderiza a página de gestão de usuários.
        Recebe o objeto 'api' (o Façade) como argumento.
    '''
    st.title("Gerenciar Usuários")
    abas = ["Cadastrar Cliente", "Excluir Cliente"]
    
    # A lógica de permissão (RF-003) está aqui
    if st.session_state.usuario_logado['Papel'] == "Administrador":
        abas.append("Cadastrar Novo Funcionário")
    
    tabs = st.tabs(abas)
    
    with tabs[0]:
        st.subheader("Cadastrar Novo Cliente")
        with st.form("novo_cliente_form", clear_on_submit=True):
            nome = st.text_input("Nome")
            cpf = st.text_input("CPF (para login)")
            end = st.text_input("Endereço")
            tel = st.text_input("Telefone")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Cadastrar Cliente"):
                msg = api.cadastrar_cliente(nome, cpf, end, tel, senha) # Chama a API
                if "Sucesso" in msg: st.success(msg)
                else: st.error(msg)

    with tabs[1]:
        st.subheader("Excluir Cliente")
        cpf_excluir = st.text_input("CPF do cliente a excluir")
       
        if st.button("Excluir Cliente", type="primary"):
            sucesso, msg = api.excluir_cliente(cpf_excluir) # Chama a API
            
            if sucesso: 
                st.success(msg)
                st.rerun()
            else: 
                st.error(msg)

    # A aba só existe se o utilizador for Admin
    if "Cadastrar Novo Funcionário" in abas:
        with tabs[2]:
            st.subheader("Cadastrar Novo Funcionário (Admin)")
            with st.form("novo_func_form", clear_on_submit=True):
                nome = st.text_input("Nome de Usuário")
                senha = st.text_input("Senha", type="password")
                papel = st.selectbox("Papel", ["Comum", "Administrador"])
                if st.form_submit_button("Cadastrar Funcionário"):
                    msg = api.cadastrar_funcionario(nome, senha, papel) # Chama a API
                    if "Sucesso" in msg: st.success(msg)
                    else: st.error(msg)