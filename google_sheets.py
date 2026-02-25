import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import datetime

# Configuration
# It's recommended to use st.secrets for these in production
# {
#   "spreadsheet_id": "YOUR_SPREADSHEET_ID",
#   "credentials_file": "credentials.json"
# }

def get_sheet():
    """Connects to Google Sheets and returns the worksheet."""
    try:
        creds_info = None
        spreadsheet_id = None

        # 1. Try to get from st.secrets (Streamlit Cloud preferred)
        if "google_sheets" in st.secrets:
            creds_info = st.secrets["google_sheets"]["credentials"]
            spreadsheet_id = st.secrets["google_sheets"].get("spreadsheet_id")
        elif "credentials" in st.secrets:
            creds_info = st.secrets["credentials"]
            spreadsheet_id = st.secrets.get("spreadsheet_id")

        if creds_info and spreadsheet_id:
            # Fix common formatting issues with private_key from secrets
            info = dict(creds_info)
            if "private_key" in info:
                info["private_key"] = info["private_key"].replace("\\n", "\n")
                
            creds = Credentials.from_service_account_info(
                info, 
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
        # 2. Try Local Fallback (credentials.json)
        elif os.path.exists("credentials.json"):
            # Use the ID provided by the user as fallback or look in st.session_state
            spreadsheet_id = "1TqWL2Q03uDAtJKkKvA8Hb2fHXwp2GrCpJXk-k1ntgMg"
            creds = Credentials.from_service_account_file(
                "credentials.json",
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
        else:
            st.error("Configuração de Google Sheets ausente. Por favor, configure os 'Secrets' no dashboard do Streamlit.")
            return None
            
        if not spreadsheet_id:
            st.error("ID da Planilha não encontrado nos segredos.")
            return None

        client = gspread.authorize(creds)
        sh = client.open_by_key(spreadsheet_id)
        return sh.get_worksheet(0)
    except Exception as e:
        st.error(f"Erro na conexão com Google Sheets: {e}")
        return None

def init_sheet():
    """Ensures the header exists in the sheet."""
    sheet = get_sheet()
    if not sheet:
        return False
    
    headers = [
        "user_key", "estudante", "email_original", "avaliador", 
        "denomine", "defina", "descreva", "de_contexto", "delimite", 
        "declare", "determine", "observacoes_col", "data_criacao"
    ]
    
    existing_headers = sheet.row_values(1)
    if not existing_headers or existing_headers != headers:
        if not existing_headers:
            sheet.append_row(headers)
        else:
            # Update the first row specifically
            sheet.update('A1:M1', [headers])
    return True

def save_evaluation(eval_data):
    """Saves or updates an evaluation in Google Sheets."""
    try:
        sheet = get_sheet()
        if not sheet:
            return False
        
        # Get all values to find if user_key already exists
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
        
        headers = [
            "user_key", "estudante", "email_original", "avaliador", 
            "denomine", "defina", "descreva", "de_contexto", "delimite", 
            "declare", "determine", "observacoes_col", "data_criacao"
        ]
        
        # Prepare row data in correct order
        row_to_save = [eval_data.get(h, "") for h in headers]
        
        if not df.empty and eval_data['user_key'] in df['user_key'].values:
            # Update existing row
            # gspread uses 1-based indexing, headers are row 1
            row_idx = df[df['user_key'] == eval_data['user_key']].index[0] + 2
            sheet.update(f'A{row_idx}:M{row_idx}', [row_to_save])
        else:
            # Append new row
            sheet.append_row(row_to_save)
        return True
    except Exception as e:
        st.error(f"Erro específico ao salvar: {e}")
        return False

def get_evaluation(user_key):
    """Retrieves an evaluation by user_key."""
    sheet = get_sheet()
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
    """Retrieves all evaluations as a pandas DataFrame."""
    sheet = get_sheet()
    if not sheet:
        return pd.DataFrame()
    
    records = sheet.get_all_records()
    return pd.DataFrame(records)
