import streamlit as st
import pandas as pd
import json
import os
import re
from datetime import datetime
import google_sheets as db

# Initialize Google Sheets (ensure headers)
db.init_sheet()

# Page Configuration
st.set_page_config(page_title="Sistema de Avaliação de Prompts", layout="wide")

# Rich Aesthetics - Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@400;600;700&display=swap');

/* ===== MODERN DESIGN SYSTEM ===== */
:root {
    /* Light Mode (Default) */
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --primary-soft: #eff6ff;
    --bg-main: #f9fafb;
    --bg-card: #ffffff;
    --text-main: #111827;
    --text-soft: #4b5563;
    --border: #e5e7eb;
    --success: #059669;
    --warning: #d97706; /* Parcialmente */
    --danger: #dc2626;
    --radius-lg: 16px;
    --radius-md: 12px;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

@media (prefers-color-scheme: dark) {
    :root {
        --primary: #3b82f6;
        --primary-hover: #60a5fa;
        --primary-soft: rgba(59, 130, 246, 0.1);
        --bg-main: #111827;
        --bg-card: #1f2937;
        --text-main: #f9fafb;
        --text-soft: #9ca3af;
        --border: #374151;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
}

/* ===== BASE STYLES ===== */
.stApp {
    background-color: var(--bg-main);
    color: var(--text-main);
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    font-family: 'Outfit', sans-serif !important;
    color: var(--text-main) !important;
    letter-spacing: -0.02em;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background-color: var(--bg-card);
    border-right: 1px solid var(--border);
}

/* ===== CARDS & CONTAINERS ===== */
div[data-testid="stForm"],
div[data-testid="stExpander"],
div.stChatMessage {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow);
}

/* ===== CHAT BUBBLES ===== */
.stChatMessage {
    padding: 1.25rem !important;
    margin-bottom: 1rem !important;
}

[data-testid="stChatMessageContent"] p {
    color: var(--text-main) !important;
    font-size: 1rem;
    line-height: 1.6;
}

/* ===== ALERTAS & BADGES ===== */
.status-badge {
    background-color: var(--success);
    color: white !important;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 10px;
    display: inline-block;
    vertical-align: middle;
}
div[role="radiogroup"] {
    background: var(--bg-main);
    border-radius: var(--radius-md);
    padding: 10px;
    border: 1px solid var(--border);
}

/* Custom Coloring for Radios based on selection (Visual Scale) */
div[role="radiogroup"] label[data-baseweb="radio"] {
    padding: 8px 12px;
    border-radius: 8px;
    transition: all 0.2s;
}

/* ===== BUTTONS ===== */
.stButton > button {
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stButton > button[kind="primary"] {
    background-color: var(--primary) !important;
    border: none !important;
}

/* Logout Button Special Style */
.logout-btn button {
    background-color: transparent !important;
    color: var(--text-soft) !important;
    border: 1px solid var(--border) !important;
    font-size: 0.85rem !important;
}

.logout-btn button:hover {
    color: var(--danger) !important;
    border-color: var(--danger) !important;
    background-color: rgba(220, 38, 38, 0.05) !important;
}

/* ===== HEADER AREA ===== */
.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

</style>
""", unsafe_allow_html=True)
# Authentication Logic
def check_password():
    """Returns `True` if the user had the correct password."""
    
    # Fallback credentials if secrets are missing
    DEFAULT_PASSWORDS = {"admin": "admin", "avaliador1": "1234", "avaliador2": "5678"}
    available_passwords = st.secrets.get("passwords", DEFAULT_PASSWORDS)

    if st.session_state.get("password_correct", False):
        return True

    st.markdown('<div class="login-header"><h1>Sistema de Avaliação de Prompts</h1><p>Acesse com suas credenciais para continuar</p></div>', unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        with st.container(border=True):
            with st.form("login_form"):
                username = st.text_input("Usuário")
                password = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar", use_container_width=True)
                
                if submit:
                    if username in available_passwords and password == available_passwords[username]:
                        st.session_state["password_correct"] = True
                        st.session_state["logged_user"] = username
                        st.rerun()
                    else:
                        st.error("😕 Usuário ou senha incorretos")
    return False

if not check_password():
    st.stop()

# ── Perfil do Avaliador (Primeira vez) ────────────────────────────────────────
# Verifica se o avaliador já preencheu o perfil (uma vez por sessão)
if "profile_complete" not in st.session_state:
    existing_profile = db.get_profile(st.session_state.logged_user)
    st.session_state["profile_complete"] = existing_profile is not None

if not st.session_state["profile_complete"]:
    # Tela de onboarding — bloqueia o acesso até preencher
    st.markdown("""
    <style>
    .profile-header { text-align: center; padding: 2rem 0 1rem; }
    .profile-header h1 { font-size: 2rem; }
    .profile-header p  { color: var(--text-soft); font-size: 1.05rem; }
    </style>
    <div class="profile-header">
        <h1>Bem-vindo ao Sistema de Avaliação 👋</h1>
        <p>Antes de começar, precisamos conhecer um pouco sobre você.<br>
           Essas informações serão salvas apenas uma vez.</p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        with st.container(border=True):
            st.subheader("Seu Perfil")
            with st.form("profile_form"):
                nome = st.text_input("Nome Completo *")
                formacao = st.text_input("Formação *",
                    placeholder="Ex: Psicologia, Medicina, Pedagogia…")
                idade = st.number_input("Idade *", min_value=18, max_value=100, step=1)
                area = st.text_input("Área de Atuação *",
                    placeholder="Ex: Saúde, Educação, Tecnologia…")
                submitted = st.form_submit_button("Salvar e Continuar →", use_container_width=True)

                if submitted:
                    errors = []
                    if not nome.strip():
                        errors.append("Nome Completo é obrigatório.")
                    if not formacao.strip():
                        errors.append("Formação é obrigatória.")
                    if not area.strip():
                        errors.append("Área de Atuação é obrigatória.")

                    if errors:
                        for e in errors:
                            st.error(e)
                    else:
                        profile_data = {
                            "usuario":       st.session_state.logged_user,
                            "nome_completo": nome.strip(),
                            "formacao":      formacao.strip(),
                            "idade":         int(idade),
                            "area_atuacao":  area.strip(),
                            "data_cadastro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                        if db.save_profile(profile_data):
                            st.session_state["profile_complete"] = True
                            st.success("Perfil salvo! Redirecionando…")
                            st.rerun()
                        else:
                            st.error("Não foi possível salvar o perfil. Tente novamente.")
    st.stop()   # impede renderizar o dashboard enquanto o perfil não está completo

# ── Dashboard de Avaliação ─────────────────────────────────────────────────────
def load_data(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_name(title):
    match = re.search(r'([^@]+)@', title)
    if match:
        name = match.group(1).title()
    else:
        name = title.split(' - ')[0].title()
    return name

def parse_messages(mapping):
    messages = []
    for node_id, node in mapping.items():
        msg_obj = node.get('message')
        if msg_obj and msg_obj.get('author') and msg_obj.get('content'):
            role = msg_obj['author']['role']
            content = msg_obj['content'].get('parts', [])
            create_time = msg_obj.get('create_time', 0)
            
            text = " ".join([str(p) for p in content if p and str(p).strip()])
            
            if text:
                messages.append({
                    'role': role,
                    'text': text,
                    'time': create_time
                })
    
    messages.sort(key=lambda x: x['time'])
    return messages

# UI Layout
# Main Header with Repositioned Sair Button
col_header, col_logout = st.columns([0.85, 0.15])
with col_header:
    st.title(f"Sistema de Avaliação de Prompts")
with col_logout:
    st.write("") # vertical spacing
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("Sair"):
        st.session_state.password_correct = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown(f"**Avaliador:** {st.session_state.logged_user}")

st.markdown("---")

data = load_data('conversations.json')

if not data:
    st.error("Arquivo 'conversations.json' não encontrado ou vazio.")
else:
    # Sidebar - Student Selection
    st.sidebar.header("Seleção de Estudante")
    
    # Get evaluated students for this evaluator
    all_evals = db.get_all_evaluations()
    evaluated_titles = []
    if not all_evals.empty:
        evaluated_titles = all_evals[all_evals['avaliador'] == st.session_state.logged_user]['email_original'].tolist()
    
    total_students = len(data)
    user_role = st.session_state.logged_user
    
    DEFAULT_PASSWORDS = {"admin": "admin", "avaliador1": "1234", "avaliador2": "5678"}
    available_passwords = st.secrets.get("passwords", DEFAULT_PASSWORDS)
    avaliadores_list = sorted([u for u in available_passwords.keys() if u.startswith("avaliador")])
    num_avaliadores = len(avaliadores_list) if avaliadores_list else 1
    
    if user_role in ["admin", "taciana"]:
        filtered_indices = range(total_students)
    elif user_role in avaliadores_list:
        idx = avaliadores_list.index(user_role)
        chunk_size = total_students // num_avaliadores
        remainder = total_students % num_avaliadores
        start = idx * chunk_size + min(idx, remainder)
        end = start + chunk_size + (1 if idx < remainder else 0)
        filtered_indices = range(start, end)
    else:
        filtered_indices = []

    # Mapa: título real → ID anonimizado ("Estudante 1", "Estudante 2", ...)
    # A ordem é estável (baseada na posição no JSON), garantindo consistência
    student_options = []           # IDs exibidos no dropdown
    student_to_title = {}          # "Estudante N" → título real
    title_to_anon = {}             # título real → "Estudante N"

    for i, conv in enumerate(data):
        title = conv.get('title', 'Sem Título')
        anon_id = f"Estudante {i+1}"
        
        if i in filtered_indices:
            student_options.append(anon_id)
            
        student_to_title[anon_id] = title
        title_to_anon[title] = anon_id

    if not student_options:
        st.warning("Nenhum estudante atribuído a você no momento.")
        st.stop()

    selected_display = st.sidebar.selectbox("Selecione o Estudante", options=student_options)
    selected_student_title = student_to_title[selected_display]
    selected_name = selected_display   # usa o ID anonimizado para exibição
    
    # Get current conversation
    selected_conv = next(conv for conv in data if conv.get('title') == selected_student_title)
    messages = parse_messages(selected_conv.get('mapping', {}))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Move "Já Avaliado" flag here as a badge
        is_evaluated = selected_student_title in evaluated_titles
        status_html = '<span class="status-badge">Já Avaliado</span>' if is_evaluated else ""
        
        st.markdown(f'<h3>Histórico de Interação: {selected_name} {status_html}</h3>', unsafe_allow_html=True)
        
        chat_container = st.container(height=600, border=True)
        with chat_container:
            for msg in messages:
                if msg['role'] == 'user':
                    st.markdown("---")
                    st.markdown("**Estudante (Prompt):**")
                    with st.chat_message("user"):
                        st.write(msg['text'])
                elif msg['role'] == 'assistant':
                    st.markdown("**IA (Resposta):**")
                    with st.chat_message("assistant"):
                        st.write(msg['text'])
    
    with col2:
        st.subheader("Critérios de Avaliação")
        
        user_key = f"{selected_student_title}_{st.session_state.logged_user}"
        
        # Load from Database
        db_eval = db.get_evaluation(user_key)
        
        pillars = [
            ("denomine", "1. Denominar uma persona"),
            ("defina", "2. Definir uma tarefa"),
            ("descreva", "3. Descrever as etapas"),
            ("de_contexto", "4. Dar contexto"),
            ("delimite", "5. Delimitar restrições"),
            ("declare", "6. Declarar o objetivo"),
            ("determine", "7. Determinar a Saída")
        ]
        
        with st.form(key=f'eval_form_{user_key}'):
            st.write("Avalie cada pilar:")
            
            p_values = {}
            for key, label in pillars:
                # Map DB values to index
                db_val = db_eval.get(key, "Pendente") if db_eval else "Pendente"
                # Updated options including 'Parcialmente'
                # Sort: Atendeu, Parcialmente, Não Atendeu, Pendente
                options = ["Atendeu", "Parcialmente", "Não Atendeu", "Pendente"]
                idx = options.index(db_val) if db_val in options else 3
                
                p_values[key] = st.radio(f"**{label}**", options, index=idx, horizontal=True)
            
            obs_val = st.text_area("Observações Gerais", value=db_eval.get('observacoes_col', "") if db_eval else "", height=100)
            
            submit = st.form_submit_button("Guardar no Google Sheets")
            
            # Validation logic
            pendentes = [p for p, v in p_values.items() if v == "Pendente"]
            
            if submit:
                if pendentes:
                    st.error(f"Por favor, complete a avaliação. Critérios pendentes: {', '.join([p.capitalize() for p in pendentes])}")
                else:
                    evaluation_entry = {
                        'user_key': user_key,
                        'estudante': selected_name,
                        'email_original': selected_student_title,
                        'avaliador': st.session_state.logged_user,
                        'observacoes_col': obs_val,
                        'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    # Add pillar ratings
                    for k, v in p_values.items():
                        evaluation_entry[k] = v
                    
                    if db.save_evaluation(evaluation_entry):
                        st.success(f"Avaliação de {selected_name} salva com sucesso no Google Sheets!")
                    else:
                        st.error("Erro ao salvar no Google Sheets. Verifique a configuração.")

    # Export Section
    st.sidebar.markdown("---")
    st.sidebar.subheader("Exportação de Dados")
    
    if st.session_state.logged_user in ["admin", "taciana"]:
        all_evals_df = db.get_all_evaluations()
        
        if not all_evals_df.empty:
            csv = all_evals_df.to_csv(index=False).encode('utf-8')
            st.sidebar.download_button(
                label="Baixar Relatório Completo (CSV)",
                data=csv,
                file_name=f"relatorio_avaliacoes_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv',
            )
            st.sidebar.info(f"Total de avaliações no banco: {len(all_evals_df)}")
        else:
            st.sidebar.warning("Nenhuma avaliação no banco de dados.")
    else:
        st.sidebar.info("Exportação restrita a administradores.")