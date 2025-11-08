import streamlit as st

# --- Definição das Páginas (Módulos) ---
# Usamos funções para modularizar o conteúdo de cada página

def page_pesquisar():
    """Página para pesquisar livros (visível para todos)."""
    st.title("Pesquisar Livros")
    st.write("Bem-vindo à página de pesquisa de livros.")
    
    st.text_input("Digite o nome do livro, autor ou gênero:")
    if st.button("Pesquisar"):
        # Lógica de pesquisa (mock)
        st.success("Resultados da pesquisa:")
        st.json({
            "livro_id": "123",
            "titulo": "O Senhor dos Anéis",
            "autor": "J.R.R. Tolkien",
            "status": "Disponível"
        })

def page_meus_emprestimos():
    """Página para o cliente ver seus empréstimos."""
    st.title("Meus Empréstimos")
    st.write(f"Olá **{st.session_state['username']}**, aqui estão seus empréstimos ativos:")
    
    # Dados mockados
    st.dataframe([
        {"Livro": "A Arte da Guerra", "Data de Empréstimo": "2025-10-20", "Data de Devolução": "2025-11-05"},
        {"Livro": "O Pequeno Príncipe", "Data de Empréstimo": "2025-10-25", "Data de Devolução": "2025-11-10"},
    ])

def page_gerenciar_emprestimos():
    """Página para o funcionário gerenciar todos os empréstimos."""
    st.title("Gerenciar Empréstimos")
    st.write("Módulo para registrar, renovar ou finalizar empréstimos de usuários.")
    
    tab1, tab2 = st.tabs(["Novo Empréstimo", "Devolução"])
    
    with tab1:
        st.text_input("ID do Cliente")
        st.text_input("ID do Livro")
        st.button("Registrar Empréstimo")
        
    with tab2:
        st.text_input("ID do Empréstimo")
        st.button("Registrar Devolução")

def page_cadastro_livros():
    """Página para o funcionário cadastrar novos livros."""
    st.title("Cadastro de Livros")
    st.write("Adicionar novos títulos ao acervo da biblioteca.")
    
    with st.form("novo_livro_form"):
        st.text_input("Título")
        st.text_input("Autor")
        st.text_input("Gênero")
        st.number_input("Quantidade em Estoque", min_value=1, value=1)
        submitted = st.form_submit_button("Cadastrar Livro")
        
        if submitted:
            st.success("Livro cadastrado com sucesso!")

def page_relatorios():
    """Página para o funcionário gerar relatórios."""
    st.title("Relatórios Gerenciais")
    st.write("Relatórios sobre o acervo e empréstimos.")
    
    if st.button("Gerar Relatório de Livros Mais Emprestados"):
        # Lógica de geração de relatório (mock)
        st.bar_chart({
            "O Senhor dos Anéis": 50,
            "1984": 45,
            "Duna": 30
        })

# --- Lógica de Login ---

def check_login(username, password, role):
    """
    Função mock para verificar o login.
    Em um app real, isso consultaria um banco de dados.
    """
    if role == "Funcionário" and username == "admin" and password == "admin123":
        return True
    if role == "Cliente" and username == "user" and password == "user123":
        return True
    return False

def show_login_page():
    """Exibe a interface de login."""
    st.set_page_config(page_title="Login - Biblioteca", layout="centered")
    st.title("Sistema de Biblioteca")
    st.subheader("Por favor, faça o login para continuar")

    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        role = st.selectbox("Papel", ["Cliente", "Funcionário"])
        
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            if check_login(username, password, role):
                # Se o login for bem-sucedido, armazena o estado na sessão
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['role'] = role
                # Força o Streamlit a rodar novamente, agora com o novo estado
                st.rerun()
            else:
                st.error("Usuário, senha ou papel incorreto!")

# --- Estrutura Principal do App ---

def show_main_app():
    """Exibe o aplicativo principal após o login."""
    st.set_page_config(page_title="Sistema de Biblioteca", layout="wide")
    
    # Dicionário de páginas
    pages = {
        "Pesquisar Livros": page_pesquisar,
        # Páginas de Cliente
        "Meus Empréstimos": page_meus_emprestimos,
        # Páginas de Funcionário
        "Gerenciar Empréstimos": page_gerenciar_emprestimos,
        "Cadastro de Livros": page_cadastro_livros,
        "Relatórios": page_relatorios,
    }

    # --- Sidebar (Barra Lateral) ---
    with st.sidebar:
        st.title("Biblioteca")
        st.write(f"Bem-vindo, **{st.session_state['username']}**!")
        st.caption(f"Papel: {st.session_state['role']}")
        st.divider()

        # Define quais módulos aparecem com base no papel (Role-Based Access)
        if st.session_state['role'] == "Cliente":
            modules = ["Pesquisar Livros", "Meus Empréstimos"]
        else: # Funcionário
            modules = ["Pesquisar Livros", "Gerenciar Empréstimos", "Cadastro de Livros", "Relatórios"]
        
        # Cria a navegação
        st.session_state['selected_page'] = st.radio(
            "Módulos", 
            modules, 
            key="page_radio"
        )
        
        st.divider()
        if st.button("Sair"):
            # Limpa o estado da sessão para fazer logout
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    # --- Conteúdo Principal ---
    # Chama a função da página selecionada
    page_function = pages.get(st.session_state['selected_page'])
    if page_function:
        page_function()

# --- Ponto de Entrada Principal ---
def main():
    # Inicializa o 'logged_in' no estado da sessão se não existir
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Decide qual interface mostrar
    if st.session_state['logged_in']:
        show_main_app()
    else:
        show_login_page()

if __name__ == "__main__":
    main()