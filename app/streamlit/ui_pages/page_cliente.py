import streamlit as st
import pandas as pd
from datetime import datetime

# --- Função Auxiliar de Formatação ---
def formatar_data(data_iso):
    ''' Converte YYYY-MM-DD para DD/MM/YYYY '''
    if not data_iso:
        return "-"
    try:
        data_obj = datetime.fromisoformat(data_iso)
        return data_obj.strftime("%d/%m/%Y")
    except ValueError:
        return data_iso

# --- Página Principal ---
def render_page_meus_emprestimos(api):
    '''
        Renderiza a página de empréstimos do cliente.
    '''
    st.header("📚 Meus Empréstimos")
    
    usuario = st.session_state.usuario_logado
    nome_cliente = usuario.get('Nome', 'Cliente')
    
    # ATENÇÃO: Certifique-se que o login salva o 'ID' (inteiro) na sessão.
    # Se o seu sistema usa CPF como chave nos empréstimos, mude para usuario['CPF']
    id_cliente = usuario.get('ID') 
    
    if not id_cliente:
        st.error("Erro de sessão: ID do usuário não encontrado.")
        return

    # 1. Busca dados no Facade
    historico = api.get_historico_cliente(id_cliente)

    if not historico:
        st.info(f"Olá, **{nome_cliente}**! Você ainda não realizou nenhum empréstimo.")
        return

    # 2. Separa Empréstimos Ativos de Finalizados
    ativos = [e for e in historico if e['Status'] in ['Em andamento', 'Atrasado']]
    finalizados = [e for e in historico if e['Status'] == 'Finalizado']

    # Criamos abas para organizar a visualização
    tab1, tab2 = st.tabs(["📖 Em Aberto", "🗃️ Histórico Completo"])

    # --- ABA 1: Empréstimos Ativos ---
    with tab1:
        if not ativos:
            st.success("Você não possui empréstimos pendentes no momento.")
        else:
            for emp in ativos:
                # Cria um container/cartão para cada empréstimo
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 2])
                    
                    with col1:
                        st.subheader(f"🔖 Empréstimo #{emp['ID_Emprestimo']}")
                        st.caption(f"Cópia ID: {emp['ID_Copia_Referencia']}")
                    
                    with col2:
                        data_prev = formatar_data(emp['DataDevolucaoPrevista'])
                        st.metric("Devolução Prevista", data_prev)
                    
                    with col3:
                        status = emp['Status']
                        if status == 'Atrasado':
                            st.error(f"⚠️ {status.upper()}")
                        else:
                            st.success(f"🟢 {status}")

                    st.divider()

                    # Área de Ações
                    col_msg, col_btn = st.columns([3, 1])
                    
                    # Lógica de Renovação
                    if status == "Atrasado":
                        col_msg.warning("Item atrasado. Renovação permitida apenas no balcão mediante pagamento de multa.")
                        col_btn.button("Renovar", disabled=True, key=f"btn_disable_{emp['ID_Emprestimo']}")
                    else:
                        col_msg.info("Renovação adiciona 7 dias úteis ao prazo.")
                        # Botão com chave única baseada no ID do empréstimo
                        if col_btn.button("🔄 Renovar", key=f"btn_renovar_{emp['ID_Emprestimo']}"):
                            sucesso, msg = api.renovar_emprestimo(emp['ID_Emprestimo'], "Cliente")
                            if sucesso:
                                st.toast("Renovação realizada com sucesso!", icon="✅")
                                st.rerun() # Atualiza a página para mostrar a nova data
                            else:
                                st.error(msg)

    # --- ABA 2: Tabela Histórica ---
    with tab2:
        st.write("Histórico de todos os seus empréstimos:")
        
        if historico:
            # Prepara dados para o DataFrame (para ficar bonito na tabela)
            df_data = []
            for item in historico:
                df_data.append({
                    "ID": item['ID_Emprestimo'],
                    "Cópia": item['ID_Copia_Referencia'],
                    "Retirada": formatar_data(item['DataInicio']),
                    "Devolução (Real)": formatar_data(item['DataDevolucaoReal']) if item['DataDevolucaoReal'] else "-",
                    "Status": item['Status']
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(
                df, 
                hide_index=True, 
                use_container_width=True,
                column_config={
                    "Status": st.column_config.TextColumn(
                        "Situação",
                        help="Estado atual do empréstimo",
                        validate="^(Em andamento|Atrasado|Finalizado)$"
                    )
                }
            )
        else:
            st.write("Nenhum registro encontrado.")