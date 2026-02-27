import os
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import datetime

# ─── Conexão com Google Sheets ────────────────────────────────────────────────

def get_sheet():
    """Conecta ao Google Sheets e retorna (worksheet_aba1, spreadsheet)."""
    try:
        creds_info = None
        spreadsheet_id = None

        if "google_sheets" in st.secrets:
            creds_info = st.secrets["google_sheets"]["credentials"]
            spreadsheet_id = st.secrets["google_sheets"].get("spreadsheet_id")
        elif "credentials" in st.secrets:
            creds_info = st.secrets["credentials"]
            spreadsheet_id = st.secrets.get("spreadsheet_id")

        if creds_info and spreadsheet_id:
            info = dict(creds_info)
            if "private_key" in info:
                info["private_key"] = info["private_key"].replace("\\n", "\n")
            creds = Credentials.from_service_account_info(
                info,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
        elif os.path.exists("credentials.json"):
            spreadsheet_id = "1TqWL2Q03uDAtJKkKvA8Hb2fHXwp2GrCpJXk-k1ntgMg"
            creds = Credentials.from_service_account_file(
                "credentials.json",
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
        else:
            st.error("Configuração de Google Sheets ausente.")
            return None, None

        if not spreadsheet_id:
            st.error("ID da Planilha não encontrado nos segredos.")
            return None, None

        client = gspread.authorize(creds)
        sh = client.open_by_key(spreadsheet_id)
        return sh.get_worksheet(0), sh
    except Exception as e:
        st.error(f"Erro na conexão com Google Sheets: {e}")
        return None, None


def get_profile_sheet():
    """Retorna a aba 'Perfil Avaliadores' (cria se não existir)."""
    try:
        _, sh = get_sheet()
        if not sh:
            return None
        try:
            ws2 = sh.get_worksheet(1)
        except Exception:
            ws2 = sh.add_worksheet(title="Perfil Avaliadores", rows=500, cols=15)
        return ws2
    except Exception as e:
        st.error(f"Erro ao acessar aba de perfis: {e}")
        return None


# ─── Campos de Perfil ─────────────────────────────────────────────────────────

PROFILE_HEADERS = [
    "usuario",
    "nome_completo",
    "formacao",
    "idade",
    "area_atuacao",
    "sexo",
    "pos_graduacao",
    "pos_graduacao_area",
    "mestrado",
    "mestrado_area",
    "tipo_uso_ia",
    "experiencia_ia",
    "data_cadastro",
]

NUM_PROFILE_COLS = len(PROFILE_HEADERS)   # 13


def get_profile(username: str):
    """
    Retorna (found, profile_dict):
      - (True,  dict)  → usuário existe (perfil preenchido)
      - (False, None)  → usuário novo (precisa preencher perfil)
      - (None,  None)  → erro de conexão (ambíguo)
    """
    ws2 = get_profile_sheet()
    if not ws2:
        return None, None
    try:
        records = ws2.get_all_records()
    except Exception as e:
        st.warning(f"Não foi possível verificar perfil: {e}")
        return None, None
    for r in records:
        if r.get("usuario") == username:
            return True, r
    return False, None


def save_profile(profile_data: dict):
    """
    Salva ou atualiza o perfil do avaliador na aba 2.
    Campos esperados: usuario, nome_completo, formacao, idade, area_atuacao,
                      sexo, pos_graduacao, experiencia_ia, data_cadastro
    """
    try:
        ws2 = get_profile_sheet()
        if not ws2:
            return False

        # Garante cabeçalhos corretos
        col_letter = chr(ord('A') + NUM_PROFILE_COLS - 1)  # 'M'
        existing_headers = ws2.row_values(1)
        if not existing_headers or existing_headers != PROFILE_HEADERS:
            if not existing_headers:
                ws2.append_row(PROFILE_HEADERS)
            else:
                ws2.update(f"A1:{col_letter}1", [PROFILE_HEADERS])

        records = ws2.get_all_records()
        row_data = [profile_data.get(h, "") for h in PROFILE_HEADERS]

        for idx, r in enumerate(records):
            if r.get("usuario") == profile_data["usuario"]:
                ws2.update(f"A{idx + 2}:{col_letter}{idx + 2}", [row_data])
                return True

        ws2.append_row(row_data)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar perfil: {e}")
        return False


# ─── Planilha Principal (Avaliações) ──────────────────────────────────────────

EVAL_HEADERS = [
    "user_key", "estudante", "email_original", "avaliador",
    "denomine", "defina", "descreva", "de_contexto", "delimite",
    "declare", "determine", "observacoes_col", "data_criacao"
]


def init_sheet():
    """Garante que o cabeçalho existe na aba 1."""
    sheet, _ = get_sheet()
    if not sheet:
        return False

    existing_headers = sheet.row_values(1)
    if not existing_headers or existing_headers != EVAL_HEADERS:
        if not existing_headers:
            sheet.append_row(EVAL_HEADERS)
        else:
            sheet.update('A1:M1', [EVAL_HEADERS])
    return True


def save_evaluation(eval_data):
    """Salva ou atualiza uma avaliação no Google Sheets."""
    try:
        sheet, _ = get_sheet()
        if not sheet:
            return False

        records = sheet.get_all_records()
        df = pd.DataFrame(records)
        row_to_save = [eval_data.get(h, "") for h in EVAL_HEADERS]

        if not df.empty and eval_data['user_key'] in df['user_key'].values:
            row_idx = df[df['user_key'] == eval_data['user_key']].index[0] + 2
            sheet.update(f'A{row_idx}:M{row_idx}', [row_to_save])
        else:
            sheet.append_row(row_to_save)
        return True
    except Exception as e:
        st.error(f"Erro específico ao salvar: {e}")
        return False


def get_evaluation(user_key):
    """Recupera uma avaliação pelo user_key."""
    sheet, _ = get_sheet()
    if not sheet:
        return None

    records = sheet.get_all_records()
    if not records:
        return None

    for record in records:
        if record.get('user_key') == user_key:
            return record
    return None


def get_all_evaluations():
    """Retorna todas as avaliações como DataFrame."""
    sheet, _ = get_sheet()
    if not sheet:
        return pd.DataFrame()

    records = sheet.get_all_records()
    return pd.DataFrame(records)
