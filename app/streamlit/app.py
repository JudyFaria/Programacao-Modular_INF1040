import streamlit as st

# --- Importa os Módulos de Lógica (Backend Puro) ---
from src.sb import gestao_usuarios as gu
from src.sb import acervo as ac
# from app import gestao_emprestimos as ge

# --- Importa os Módulos de UI (Frontend) ---
from ui_pages import page_public
from ui_pages import page_cliente
from ui_pages import page_funcionario

# --- Ponto de Entrada Principal ---

def main():
    st.set_page_config(page_title="Sistema de Biblioteca", layout="wide")
    
    # 1. Garante que o estado seja inicializado APENAS UMA VEZ
    inicializar_estado_sessao()

    # 2. Define o mapa de quais páginas existem
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
    
    # 3. Desenha a Barra Lateral (Sidebar)
    with st.sidebar:
        st.title("Biblioteca")
        
        if not st.session_state.logged_in:
            render_sidebar_login()
            st.session_state.selected_page = "Pesquisar Acervo"
        else:
            render_sidebar_nav_e_logout(pages)

    # 4. Desenha o Conteúdo Principal da Página
    page_name = st.session_state.get('selected_page', "Pesquisar Acervo")
    page_function = pages.get(page_name)
    
    if page_function:
        page_function()
    else:
        st.error("Página não encontrada.")

# --- Funções Auxiliares (Estado e Sidebar) ---

def inicializar_estado_sessao():
    """
    Cria o "Banco de Dados" da aplicação no st.session_state.
    Isto é o que será passado para as funções de backend.
    """
    if 'estado_inicializado' not in st.session_state:
        # Estado de Login
        st.session_state.logged_in = False
        st.session_state.usuario_logado = None
        st.session_state.selected_page = "Pesquisar Acervo"
        
        # --- O "Banco de Dados" que o backend irá usar ---
        # Acervo
        st.session_state._lst_livros = []
        st.session_state._lst_copias_livros = []
        st.session_state._prox_id_livro = 1
        st.session_state._prox_id_copia = 1
        
        # Usuários
        st.session_state._lst_funcionarios = []
        st.session_state._lst_clientes = []
        st.session_state._prox_id_funcionario = 1
        st.session_state._prox_id_cliente = 1
        
        # Empréstimos (para RF-009)
        st.session_state._lst_emprestimos = []
        
        # Estado inicializado
        st.session_state.estado_inicializado = True
        
        # --- Chama o backend para criar o admin padrão ---
        # O backend modifica as listas e devolve-as
        (
            st.session_state._lst_funcionarios,
            st.session_state._prox_id_funcionario,
            _ # admin_criado
        ) = gu.inicializar_admin_padrao(
            st.session_state._lst_funcionarios,
            st.session_state._prox_id_funcionario
        )
        
        # --- DADOS DE EXEMPLO PARA TESTE ---
        # O frontend gere o estado
        
        # Cadastra Livro 1
        (
            st.session_state._lst_livros,
            st.session_state._prox_id_livro,
            livro_1
        ) = ac.cadastrar_livro("O Senhor dos Anéis", "J.R.R. Tolkien", "HarperCollins", 
                                st.session_state._lst_livros, 
                                st.session_state._prox_id_livro)
        
        # Adiciona cópias ao Livro 1
        if livro_1:
            (
                st.session_state._lst_copias_livros,
                st.session_state._prox_id_copia,
                _ # copias_criadas
            ) = ac.add_copias(livro_1["ID_Livro"], 3, "Corredor 1-A", 
                                st.session_state._lst_livros, 
                                st.session_state._lst_copias_livros, 
                                st.session_state._prox_id_copia)

        # Cadastra Livro 2
        (
            st.session_state._lst_livros,
            st.session_state._prox_id_livro,
            livro_2
        ) = ac.cadastrar_livro("Duna", "Frank Herbert", "Editora Aleph", 
                                st.session_state._lst_livros, 
                                st.session_state._prox_id_livro)
        
        # Adiciona cópias ao Livro 2
        if livro_2:
            (
                st.session_state._lst_copias_livros,
                st.session_state._prox_id_copia,
                _ # copias_criadas
            ) = ac.add_copias(livro_2["ID_Livro"], 2, "Corredor 1-B", 
                                st.session_state._lst_livros, 
                                st.session_state._lst_copias_livros, 
                                st.session_state._prox_id_copia)
        
        # Cadastra Cliente
        (
            st.session_state._lst_clientes,
            st.session_state._prox_id_cliente,
            _ # cliente_criado
        ) = gu.cadastrar_cliente("Ana Silva", "111", "Rua A", "9999", "ana123",
                                st.session_state._lst_clientes,
                                st.session_state._prox_id_cliente)

def render_sidebar_login():
    """Mostra o formulário de login na sidebar."""
    st.subheader("Login")
    with st.form("sidebar_login_form"):
        username = st.text_input("Usuário (CPF ou Admin)")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            # O backend 'autenticar' não modifica o estado, só lê
            usuario = gu.autenticar(
                username, password,
                st.session_state._lst_funcionarios,
                st.session_state._lst_clientes
            )
            
            if usuario:
                st.session_state.logged_in = True
                st.session_state.usuario_logado = usuario
                
                if usuario['tipo'] == 'Cliente':
                    st.session_state.selected_page = "Meus Empréstimos"
                else:
                    st.session_state.selected_page = "Gerenciar Acervo"
                
                st.rerun()
            else:
                st.error("Usuário ou senha incorreto!")

def render_sidebar_nav_e_logout(todas_as_paginas):
    """Mostra o menu de navegação e o botão de sair."""
    
    usuario = st.session_state.usuario_logado
    st.write(f"Bem-vindo(a), **{usuario['nome_usuario']}**!")
    st.caption(f"Papel: {usuario['tipo']} ({usuario.get('papel', 'N/A')})")
    st.divider()

    if usuario['tipo'] == "Cliente":
        modulos_visiveis = ["Pesquisar Acervo", "Meus Empréstimos"]
    elif usuario['tipo'] == "Funcionário":
        modulos_visiveis = ["Pesquisar Acervo", "Gerenciar Acervo", "Gerenciar Usuários"]
    else:
        modulos_visiveis = ["Pesquisar Acervo"]

    opcoes_radio = {nome: func for nome, func in todas_as_paginas.items() if nome in modulos_visiveis}
    
    index_atual = 0
    page_selecionada = st.session_state.get('selected_page', "Pesquisar Acervo")
    if page_selecionada in opcoes_radio.keys():
        index_atual = list(opcoes_radio.keys()).index(page_selecionada)

    st.session_state.selected_page = st.radio(
        "Módulos", 
        opcoes_radio.keys(), 
        key="page_radio",
        index=index_atual
    )
    
    st.divider()
    if st.button("Sair"):
        # Guarda as listas (o "banco de dados")
        db_keys = [
            'estado_inicializado', '_lst_livros', '_lst_copias_livros', 
            '_lst_funcionarios', '_lst_clientes', '_lst_emprestimos',
            '_prox_id_livro', '_prox_id_copia', '_prox_id_funcionario',
            '_prox_id_cliente'
        ]
        db_data = {key: st.session_state[key] for key in db_keys if key in st.session_state}
        
        # Limpa tudo
        st.session_state.clear()
        
        # Restaura o "banco de dados"
        for key, value in db_data.items():
            st.session_state[key] = value
            
        # Reseta o login
        st.session_state.logged_in = False
        st.session_state.usuario_logado = None
        st.session_state.selected_page = "Pesquisar Acervo"
        st.rerun()

# --- Ponto de Entrada Padrão do Python ---
if __name__ == "__main__":
    main()