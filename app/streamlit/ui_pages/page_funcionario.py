import streamlit as st
import pandas as pd

def render_page_gerenciar_acervo(api):
    '''
        Renderiza a página de gestão de acervo.
        Recebe o objeto 'api' (o Façade) como argumento.
    '''
    st.title("Gerenciar Acervo (Livros e Exemplares)")
    tab1, tab2, tab3 = st.tabs(["Cadastrar Novo Título", "Adicionar Exemplares", "Excluir Livro"])

    with tab1:
        st.subheader("Cadastrar Novo Título e Exemplares Iniciais")
        with st.form("novo_livro_form", clear_on_submit=True):
            titulo = st.text_input("Título")
            autor = st.text_input("Autor")
            edicao = st.text_input("Edição/Editora")
            st.divider()
            quantidade = st.number_input("Qtd. Exemplares", min_value=1, value=1)
            localizacao = st.text_input("Localização")
            
            if st.form_submit_button("Cadastrar Título e Exemplares"):
                
                livro = api.cadastrar_livro(titulo, autor, edicao) # Chama a API
                
                if not livro:
                    st.error(f"Erro ao cadastrar livro '{titulo}'.")
                else:
                    copia = api.add_copias(livro["ID_Livro"], quantidade, localizacao) # Chama a API
                    if copia:
                        st.success(f"Livro '{livro['Titulo']}' e {quantidade} exemplar(es) cadastrados!")
                    else:
                        st.error("Erro ao adicionar exemplares.")

    with tab2:
        st.subheader("Adicionar Exemplares a um Título Existente")
        livros = api.get_todos_livros() # Chama a API
        if not livros:
            st.warning("Nenhum livro cadastrado.")
        else:
            opcoes = {f"ID {l['ID_Livro']}: {l['Titulo']}": l['ID_Livro'] for l in livros}
            selecionado = st.selectbox("Selecione o livro", ["Selecione..."] + list(opcoes.keys()))
            if selecionado != "Selecione...":
                id_livro = opcoes[selecionado]
                with st.form("add_exemplares_form", clear_on_submit=True):
                    qtd = st.number_input("Qtd. Novos Exemplares", min_value=1, value=1)
                    loc = st.text_input("Localização")
                    if st.form_submit_button("Adicionar Exemplares"):
                        _, status = api.add_copias(id_livro, qtd, loc) # Chama a API
                        if status == "sucesso": 
                            st.success("Exemplares adicionados!")
                        else: 
                            st.error("Erro ao adicionar exemplares.")

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
                    exclusao = api.excluir_livro(id_excluir) # Chama a API
                    if exclusao: 
                        st.success("Livro excluído com sucesso.")
                        st.rerun() # Atualiza a UI para remover o livro da lista
                    else: 
                        st.error("Erro ao excluir livro.")

def render_page_gerenciar_usuarios(api):
    '''
        Renderiza a página de gestão de usuários.
        Recebe o objeto 'api' (o Façade) como argumento.
    '''
    st.title("Gerenciar Usuários")
    abas = ["Clientes", "Cadastrar Cliente", "Excluir Cliente"]
    
    # A lógica de permissão (RF-003) está aqui
    if st.session_state.usuario_logado['Papel'] == "Administrador":
        abas.append("Cadastrar Novo Funcionário")
        abas.append("Excluir Funcionáios")
    
    tabs = st.tabs(abas)
    
    with tabs[0]:
        st.subheader("Lista de Clientes Cadastrados")
        clientes = api.get_todos_clientes() # Chama a API
        
        if not clientes:
            st.info("Nenhum cliente cadastrado.")
        else:
            df_clientes = pd.DataFrame(clientes)
            st.dataframe(df_clientes, hide_index=True)

        
    with tabs[1]:
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

    with tabs[2]:
        st.subheader("Excluir Cliente")
        cpf_excluir = st.text_input("CPF do cliente a excluir")
       
        if st.button("Excluir Cliente", type="primary"):
            sucesso, msg = api.excluir_cliente(cpf_excluir) # Chama a API
            
            if sucesso: 
                st.success(msg)
                st.rerun()
            else: 
                st.error(msg)

    # Essas abas só existe se o utilizador for Admin
    if "Cadastrar Novo Funcionário" in abas:
        
        with tabs[3]:
            st.subheader("Cadastrar Novo Funcionário (Admin)")
            with st.form("novo_func_form", clear_on_submit=True):
                nome = st.text_input("Nome de Usuário")
                senha = st.text_input("Senha", type="password")
                papel = st.selectbox("Papel", ["Comum", "Administrador"])
                if st.form_submit_button("Cadastrar Funcionário"):
                    msg = api.cadastrar_funcionario(nome, senha, papel) # Chama a API
                    if "Sucesso" in msg: st.success(msg)
                    else: st.error(msg)

        with tabs[4]:
            st.subheader("Excluir Funcionário (Admin)")
            funcionarios = api.get_todos_funcionarios() # Chama a API
            
            if not funcionarios:
                st.info("Nenhum funcionário cadastrado.")
            else:
                opcoes_func = {f"{f['NomeUsuario']} (Papel: {f['Papel']})": f['NomeUsuario'] for f in funcionarios}
                selecionado_func = st.selectbox("Selecione o funcionário a excluir", ["Selecione..."] + list(opcoes_func.keys()))
                
                if selecionado_func != "Selecione...":
                    nome_excluir = opcoes_func[selecionado_func]
                    
                    if st.button(f"Confirmar Exclusão de '{selecionado_func}'", type="primary"):
                        sucesso, msg = api.excluir_funcionario(nome_excluir) # Chama a API
                        
                        if sucesso: 
                            st.success(msg)
                            st.rerun()
                        else: 
                            st.error(msg)


def render_page_gerenciar_emprestimos(api):
    '''
    Página do Balcão de Atendimento (Realizar Empréstimo e Devolução)
    '''
    st.title("🛎️ Balcão de Empréstimos")
    
    tab_emp, tab_dev = st.tabs(["📤 Realizar Empréstimo", "📥 Registrar Devolução"])

    # --- ABA 1: REALIZAR EMPRÉSTIMO ---
    with tab_emp:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Nova Operação")
            
            # Passo 1: Validar Cliente (Busca por CPF)
            cpf_input = st.text_input("CPF do Cliente", placeholder="Apenas números", key="cpf_emp_input")
            cliente_valido = None
            
            if cpf_input:
                # Aqui estava o erro: usamos a busca por CPF, não o histórico
                cliente_valido = api.buscar_cliente_por_cpf(cpf_input)
                
                if cliente_valido:
                    st.success(f"Cliente Identificado: **{cliente_valido['Nome']}**")
                else:
                    st.error("Cliente não encontrado.")

            st.divider()

            # Passo 2: Validar Exemplar (Busca por ID)
            id_exemplar = st.number_input("ID da Exemplar", min_value=0, step=1, key="id_exemplar_emp")
            exemplar_valido = None
            
            if id_exemplar > 0:
                exemplar_valido = api.get_copia_por_id(id_exemplar)
                if exemplar_valido:
                    status = exemplar_valido['Status']
                    titulo = exemplar_valido.get('Titulo_Livro', 'Desconhecido')
                    
                    if status == "Disponível":
                        st.info(f"📖 Livro: **{titulo}**\n\n✅ Status: Disponível")
                    else:
                        st.warning(f"📖 Livro: **{titulo}**\n\n⚠️ Status: {status}")
                else:
                    st.caption("Exemplar não encontrado no acervo.")

            st.divider()

            # Passo 3: Botão de Ação
            # Habilita apenas se Cliente OK + Exemplar OK + Status Disponível
            pode_emprestar = (cliente_valido is not None) and (exemplar_valido is not None) and (exemplar_valido['Status'] == 'Disponível')
            
            if st.button("Confirmar Empréstimo", type="primary", disabled=not pode_emprestar):
                sucesso, msg = api.criar_emprestimo(cliente_valido['ID_Cliente'], id_exemplar)
                if sucesso:
                    st.balloons()
                    st.success(msg)
                else:
                    st.error(msg)

        # Coluna da Direita: Tabela de apoio
        with col2:
            st.caption("Itens disponíveis no Acervo:")
            lista_disp = api.get_copias_disponiveis_simples()
            if lista_disp:
                # Usa DataFrame para visualização tabular bonita
                df = pd.DataFrame(lista_disp)
                st.dataframe(df, hide_index=True, height=400)
            else:
                st.info("Nenhum item disponível no momento.")

    # --- ABA 2: REGISTRAR DEVOLUÇÃO ---
    with tab_dev:
        st.subheader("Recebimento de Material")
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            id_dev = st.number_input("ID do Exemplar Devolvido", min_value=0, step=1, key="id_exemplar_dev")
            
            if st.button("Confirmar Devolução", type="secondary"):
                if id_dev > 0:
                    sucesso, msg = api.registrar_devolucao(id_dev)
                    if sucesso:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Insira um ID válido.")