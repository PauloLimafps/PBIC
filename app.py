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

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@400;600;700&display=swap');

:root {
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --primary-soft: #eff6ff;
    --bg-main: #f9fafb;
    --bg-card: #ffffff;
    --text-main: #111827;
    --text-soft: #4b5563;
    --border: #e5e7eb;
    --success: #059669;
    --warning: #d97706;
    --danger: #dc2626;
    --radius-lg: 16px;
    --radius-md: 12px;
    --shadow: 0 4px 6px -1px rgba(0,0,0,.1), 0 2px 4px -1px rgba(0,0,0,.06);
}

@media (prefers-color-scheme: dark) {
    :root {
        --primary: #3b82f6;
        --primary-hover: #60a5fa;
        --primary-soft: rgba(59,130,246,.1);
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

.stApp { background-color: var(--bg-main); color: var(--text-main); font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Outfit', sans-serif !important; color: var(--text-main) !important; letter-spacing: -.02em; }

[data-testid="stSidebar"] { background-color: var(--bg-card); border-right: 1px solid var(--border); }

div[data-testid="stForm"],
div[data-testid="stExpander"],
div.stChatMessage {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow);
}

.stChatMessage { padding: 1.25rem !important; margin-bottom: 1rem !important; }
[data-testid="stChatMessageContent"] p { color: var(--text-main) !important; font-size: 1rem; line-height: 1.6; }

.status-badge {
    background-color: var(--success);
    color: white !important;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: .75rem;
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

div[role="radiogroup"] label[data-baseweb="radio"] {
    padding: 8px 12px;
    border-radius: 8px;
    transition: all .2s;
}

.stButton > button {
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important;
    transition: all .2s cubic-bezier(.4,0,.2,1) !important;
}

.stButton > button[kind="primary"] {
    background-color: var(--primary) !important;
    border: none !important;
}

.logout-btn button {
    background-color: transparent !important;
    color: var(--text-soft) !important;
    border: 1px solid var(--border) !important;
    font-size: .85rem !important;
}

.logout-btn button:hover {
    color: var(--danger) !important;
    border-color: var(--danger) !important;
    background-color: rgba(220,38,38,.05) !important;
}

/* ── Tela de Acesso ── */
.access-header {
    text-align: center;
    padding: 3rem 0 2rem;
}
.access-header h1 {
    font-size: 2.4rem;
    background: linear-gradient(135deg, var(--primary) 0%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: .5rem;
}
.access-header p { color: var(--text-soft); font-size: 1.05rem; }
</style>
""", unsafe_allow_html=True)

# ── Usuários com visão total ───────────────────────────────────────────────────
ADMIN_USERS = ["admin", "taciana"]

# ── Tela de Acesso (sem senha) ─────────────────────────────────────────────────
def check_access():
    """
    Tela inicial simples: usuário digita seu nome de login.
    Sem senha — qualquer nome é válido (exceto vazio).
    Retorna True se o usuário já está logado.
    """
    if st.session_state.get("logged_user"):
        return True

    st.markdown(
        '<div class="access-header">'
        '<h1>🎓 Sistema de Avaliação de Prompts</h1>'
        '<p>Digite seu nome de usuário para acessar o sistema.<br>'
        'Se for seu primeiro acesso, você será guiado pelo cadastro.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_l, col_m, col_r = st.columns([1, 1.6, 1])
    with col_m:
        with st.container(border=True):
            st.markdown("#### Identificação")
            username_input = st.text_input(
                "Nome de usuário",
                placeholder="Ex: maria.silva",
                key="username_input_field",
                help="Use um nome simples, sem espaços. Será sua identificação no sistema."
            )
            st.caption("ℹ️ Sem maiúsculas ou espaços — use ponto ou sublinhado se precisar separar palavras.")

            enter = st.button("Entrar →", use_container_width=True, type="primary")

            if enter:
                u = username_input.strip().lower().replace(" ", "_")
                if not u:
                    st.error("Por favor, informe seu nome de usuário.")
                else:
                    st.session_state["logged_user"] = u
                    st.rerun()

    return False

if not check_access():
    st.stop()

# ── Verificação / Cadastro de Perfil ──────────────────────────────────────────
if "profile_complete" not in st.session_state:
    with st.spinner("Verificando seu cadastro…"):
        found, profile_data = db.get_profile(st.session_state.logged_user)
    if found is True:
        st.session_state["profile_complete"] = True
        # Busca e cacheia a posição sequencial do usuário (para distribuição de estudantes)
        if "user_order" not in st.session_state and st.session_state.logged_user not in ADMIN_USERS:
            st.session_state["user_order"] = db.get_user_order_index(
                st.session_state.logged_user, ADMIN_USERS
            )
    elif found is False:
        st.session_state["profile_complete"] = False
    else:
        st.session_state["profile_complete"] = None   # erro de conexão

if st.session_state.get("profile_complete") is None:
    st.warning("⚠️ Não foi possível verificar seu cadastro. Verifique sua conexão.")
    if st.button("🔄 Tentar Novamente"):
        del st.session_state["profile_complete"]
        st.rerun()
    st.stop()

# ── Formulário de Perfil (1ª vez) ─────────────────────────────────────────────
if st.session_state["profile_complete"] is False:
    st.markdown("""
    <style>
    .profile-header { text-align: center; padding: 2rem 0 1rem; }
    .profile-header h1 { font-size: 2rem; }
    .profile-header p  { color: var(--text-soft); font-size: 1.05rem; }
    </style>
    <div class="profile-header">
        <h1>👋 Bem-vindo ao Sistema de Avaliação!</h1>
        <p>Antes de começar, precisamos conhecer um pouco sobre você.<br>
           Essas informações serão salvas apenas uma vez.</p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        with st.container(border=True):
            st.subheader(f"Perfil do Avaliador — @{st.session_state.logged_user}")
            with st.form("profile_form"):

                st.markdown("**📋 Dados Pessoais**")
                nome = st.text_input("Nome Completo *", placeholder="Seu nome completo")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    idade = st.number_input("Idade *", min_value=16, max_value=100, step=1, value=25)
                with col_b:
                    sexo = st.radio(
                        "Sexo *",
                        ["Masculino", "Feminino", "Prefiro não informar"],
                        horizontal=True,
                        index=2,
                    )

                st.markdown("---")
                st.markdown("**🎓 Formação & Experiência**")

                formacao = st.text_input(
                    "Formação *",
                    placeholder="Ex: Psicologia, Medicina, Pedagogia…"
                )
                area = st.text_input(
                    "Área de Atuação *",
                    placeholder="Ex: Saúde, Educação, Tecnologia…"
                )

                # ── Pós-graduação ──────────────────────────────────────────
                pos_graduacao = st.radio(
                    "Possui Pós-graduação (especialização/lato sensu)?",
                    ["Sim", "Não"],
                    horizontal=True,
                    index=1,
                )
                pos_graduacao_area = st.text_input(
                    "Área da Pós-graduação",
                    placeholder="Ex: Educação Especial, Gestão em Saúde… (deixe em branco se não tiver)",
                )

                # ── Mestrado ────────────────────────────────────────────────
                mestrado = st.radio(
                    "Possui Mestrado (stricto sensu)?",
                    ["Sim", "Não"],
                    horizontal=True,
                    index=1,
                )
                mestrado_area = st.text_input(
                    "Área do Mestrado",
                    placeholder="Ex: Ciências da Computação, Linguística… (deixe em branco se não tiver)",
                )

                st.markdown("---")
                st.markdown("**🤖 Experiência com Inteligência Artificial**")

                tipo_uso_ia = st.radio(
                    "Como você utiliza IA? *",
                    [
                        "Uso recreativo / pessoal",
                        "Uso para desenvolvimento / trabalho",
                        "Ambos (recreativo e desenvolvimento)",
                    ],
                    index=0,
                    help="Selecione o que melhor descreve seu perfil de uso de IA."
                )

                experiencia_ia = st.selectbox(
                    "Tempo de experiência com IA *",
                    [
                        "Menos de 1 ano",
                        "1-2 anos",
                        "3-5 anos",
                        "Mais de 5 anos",
                    ],
                    index=0,
                )

                submitted = st.form_submit_button("Salvar e Continuar →", use_container_width=True)

            if submitted:
                errors = []
                if not nome.strip():
                    errors.append("Nome Completo é obrigatório.")
                if not formacao.strip():
                    errors.append("Formação é obrigatória.")
                if not area.strip():
                    errors.append("Área de Atuação é obrigatória.")
                if pos_graduacao == "Sim" and not pos_graduacao_area.strip():
                    errors.append("Informe a área da Pós-graduação.")
                if mestrado == "Sim" and not mestrado_area.strip():
                    errors.append("Informe a área do Mestrado.")

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    profile_payload = {
                        "usuario":            st.session_state.logged_user,
                        "nome_completo":      nome.strip(),
                        "formacao":           formacao.strip(),
                        "idade":              int(idade),
                        "area_atuacao":       area.strip(),
                        "sexo":               sexo,
                        "pos_graduacao":      pos_graduacao,
                        "pos_graduacao_area": pos_graduacao_area.strip() if pos_graduacao == "Sim" else "N/A",
                        "mestrado":           mestrado,
                        "mestrado_area":      mestrado_area.strip() if mestrado == "Sim" else "N/A",
                        "tipo_uso_ia":        tipo_uso_ia,
                        "experiencia_ia":     experiencia_ia,
                        "data_cadastro":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    if db.save_profile(profile_payload):
                        st.session_state["profile_complete"] = True
                        # Cacheia a posição sequencial para distribuição de estudantes
                        if st.session_state.logged_user not in ADMIN_USERS:
                            st.session_state["user_order"] = db.get_user_order_index(
                                st.session_state.logged_user, ADMIN_USERS
                            )
                        st.success("✅ Perfil salvo! Redirecionando…")
                        st.rerun()
                    else:
                        st.error("Não foi possível salvar o perfil. Tente novamente.")

    st.stop()   # bloqueia o app enquanto o perfil não está completo

# ── Funções auxiliares ─────────────────────────────────────────────────────────
def load_data(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_messages(mapping):
    messages = []
    for node_id, node in mapping.items():
        msg_obj = node.get('message')
        if msg_obj and msg_obj.get('author') and msg_obj.get('content'):
            role = msg_obj['author']['role']
            content = msg_obj['content'].get('parts', [])
            create_time = msg_obj.get('create_time') or 0
            text = " ".join([str(p) for p in content if p and str(p).strip()])
            if text:
                messages.append({'role': role, 'text': text, 'time': create_time})
    messages.sort(key=lambda x: (x['time'] or 0))
    return messages


def get_student_indices(username: str, total: int) -> range:
    """
    Distribuição sequencial por ordem de cadastro, grupos de 10.
    - admin / taciana → todos os estudantes
    - 1º usuário cadastrado → estudantes 1-10
    - 2º usuário → 11-20
    - ... e quando acabar os grupos, volta do início (rotação circular)
    A ordem sequencial é lida do Google Sheets (session_state faz cache).
    """
    if username in ADMIN_USERS:
        return range(total)
    GROUP_SIZE = 10
    num_groups = max(1, total // GROUP_SIZE)
    # user_order é cacheado na session_state para evitar chamada extra ao Sheets
    user_order = st.session_state.get("user_order", 0)
    group_idx = user_order % num_groups
    start = group_idx * GROUP_SIZE
    end   = min(start + GROUP_SIZE, total)
    return range(start, end)


# ── Header + Logout ────────────────────────────────────────────────────────────
col_header, col_logout = st.columns([0.85, 0.15])
with col_header:
    st.title("Sistema de Avaliação de Prompts")
with col_logout:
    st.write("")
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("Sair"):
        for key in ["logged_user", "profile_complete"]:
            st.session_state.pop(key, None)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown(f"**Avaliador:** {st.session_state.logged_user}")
if st.session_state.logged_user in ADMIN_USERS:
    st.sidebar.markdown("🔑 *Acesso total*")

st.markdown("---")

# ── Dados & Distribuição ───────────────────────────────────────────────────────
data = load_data('conversations.json')

if not data:
    st.error("Arquivo 'conversations.json' não encontrado ou vazio.")
else:
    st.sidebar.header("Seleção de Estudante")

    # Avaliações já feitas por este avaliador
    all_evals = db.get_all_evaluations()
    evaluated_titles = []
    if not all_evals.empty:
        evaluated_titles = (
            all_evals[all_evals['avaliador'] == st.session_state.logged_user]
            ['email_original'].tolist()
        )

    total_students = len(data)
    filtered_indices = get_student_indices(st.session_state.logged_user, total_students)

    # Mapa: ID anônimo ↔ título real
    student_options = []
    student_to_title = {}

    for i, conv in enumerate(data):
        title = conv.get('title', 'Sem Título')
        anon_id = f"Estudante {i + 1}"
        student_to_title[anon_id] = title
        if i in filtered_indices:
            student_options.append(anon_id)

    if not student_options:
        st.warning("Nenhum estudante atribuído a você no momento.")
        st.stop()

    selected_display = st.sidebar.selectbox("Selecione o Estudante", options=student_options)
    selected_student_title = student_to_title[selected_display]
    selected_name = selected_display

    selected_conv = next(conv for conv in data if conv.get('title') == selected_student_title)
    messages = parse_messages(selected_conv.get('mapping', {}))

    col1, col2 = st.columns([2, 1])

    with col1:
        is_evaluated = selected_student_title in evaluated_titles
        status_html = '<span class="status-badge">Já Avaliado</span>' if is_evaluated else ""
        st.markdown(f'<h3>Histórico de Interação: {selected_name} {status_html}</h3>',
                    unsafe_allow_html=True)

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
        db_eval  = db.get_evaluation(user_key)

        pillars = [
            ("denomine",   "1. Denominar uma persona"),
            ("defina",     "2. Definir uma tarefa"),
            ("descreva",   "3. Descrever as etapas"),
            ("de_contexto","4. Dar contexto"),
            ("delimite",   "5. Delimitar restrições"),
            ("declare",    "6. Declarar o objetivo"),
            ("determine",  "7. Determinar a Saída"),
        ]

        with st.form(key=f'eval_form_{user_key}'):
            st.write("Avalie cada pilar:")
            options = ["Atendeu", "Parcialmente", "Não Atendeu", "Pendente"]
            p_values = {}
            for key, label in pillars:
                db_val = db_eval.get(key, "Pendente") if db_eval else "Pendente"
                idx = options.index(db_val) if db_val in options else 3
                p_values[key] = st.radio(f"**{label}**", options, index=idx, horizontal=True)

            obs_val = st.text_area(
                "Observações Gerais",
                value=db_eval.get('observacoes_col', "") if db_eval else "",
                height=100,
            )
            submit = st.form_submit_button("Guardar no Google Sheets")

            pendentes = [p for p, v in p_values.items() if v == "Pendente"]

            if submit:
                if pendentes:
                    st.error(f"Critérios pendentes: {', '.join([p.capitalize() for p in pendentes])}")
                else:
                    evaluation_entry = {
                        'user_key':       user_key,
                        'estudante':      selected_name,
                        'email_original': selected_student_title,
                        'avaliador':      st.session_state.logged_user,
                        'observacoes_col':obs_val,
                        'data_criacao':   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    for k, v in p_values.items():
                        evaluation_entry[k] = v

                    if db.save_evaluation(evaluation_entry):
                        st.success(f"✅ Avaliação de {selected_name} salva com sucesso!")
                    else:
                        st.error("Erro ao salvar no Google Sheets. Verifique a configuração.")

    # ── Exportação (somente admin/taciana) ─────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.subheader("Exportação de Dados")

    if st.session_state.logged_user in ADMIN_USERS:
        all_evals_df = db.get_all_evaluations()
        if not all_evals_df.empty:
            csv = all_evals_df.to_csv(index=False).encode('utf-8')
            st.sidebar.download_button(
                label="Baixar Relatório Completo (CSV)",
                data=csv,
                file_name=f"relatorio_avaliacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv',
            )
            st.sidebar.info(f"Total de avaliações: {len(all_evals_df)}")
        else:
            st.sidebar.warning("Nenhuma avaliação registrada ainda.")
    else:
        st.sidebar.info("Exportação restrita a administradores.")