# 🎓 Sistema de Avaliação de Prompts — PBIC

Aplicação web desenvolvida com **Streamlit** para avaliação de interações de estudantes com ferramentas de Inteligência Artificial. Os avaliadores analisam os prompts submetidos pelos alunos com base em sete critérios pedagógicos estruturados.

---

## ✨ Funcionalidades

- **Acesso sem senha** — qualquer avaliador cria seu próprio usuário pelo link do app
- **Cadastro de perfil na primeira vez** — dados pessoais, formação e experiência com IA
- **Distribuição automática de estudantes** — cada avaliador recebe uma fatia consistente via hash do nome de usuário
- **Avaliação por 7 pilares** — critérios baseados no framework de prompts pedagógicos
- **Persistência no Google Sheets** — avaliações e perfis salvos em tempo real
- **Exportação CSV** — disponível para administradores (`admin` e `taciana`)

---

## 🏗️ Estrutura do Projeto

```
PBIC/
├── app.py                  # Aplicativo principal Streamlit
├── google_sheets.py        # Integração com Google Sheets (perfis + avaliações)
├── conversations.json      # Base de interações dos estudantes
├── requirements.txt        # Dependências Python
├── .streamlit/
│   ├── config.toml         # Configurações do servidor Streamlit
│   └── secrets.toml        # Credenciais (NÃO vai ao GitHub)
└── .gitignore
```

---

## 👤 Fluxo de Acesso

```
Acessa o app
    ↓
Digite seu nome de usuário (sem senha)
    ↓
┌─────────────────────┬──────────────────────────┐
│  Usuário NOVO       │  Usuário EXISTENTE        │
│  → Formulário de    │  → Vai direto para        │
│    perfil (1x só)   │    o app de avaliação     │
└─────────────────────┴──────────────────────────┘
```

### Perfil de Acesso

| Usuário | Visibilidade |
|---------|-------------|
| `admin` | Todos os estudantes + exportar CSV |
| `taciana` | Todos os estudantes + exportar CSV |
| Qualquer outro | Grupo fixo de ~20 estudantes (baseado no hash do nome) |

---

## 📋 Formulário de Perfil (preenchido uma única vez)

| Campo | Tipo |
|-------|------|
| Nome Completo | Texto |
| Idade | Número |
| Sexo | Masculino / Feminino / Prefiro não informar |
| Formação | Texto |
| Área de Atuação | Texto |
| Possui Pós-graduação (especialização/lato sensu)? | Sim / Não |
| Área da Pós-graduação | Texto |
| Possui Mestrado (stricto sensu)? | Sim / Não |
| Área do Mestrado | Texto |
| Como você utiliza IA? | Recreativo / Desenvolvimento / Ambos |
| Tempo de experiência com IA | < 1 ano / 1-2 anos / 3-5 anos / > 5 anos |

---

## ⚖️ Critérios de Avaliação (7 Pilares)

Cada estudante é avaliado nos seguintes critérios, com as opções:  
**Atendeu** / **Parcialmente** / **Não Atendeu**

| # | Pilar |
|---|-------|
| 1 | Denominar uma persona |
| 2 | Definir uma tarefa |
| 3 | Descrever as etapas |
| 4 | Dar contexto |
| 5 | Delimitar restrições |
| 6 | Declarar o objetivo |
| 7 | Determinar a Saída |

---

## 🚀 Rodando Localmente

### Pré-requisitos
- Python 3.9+
- Conta no Google Cloud com Service Account e acesso à planilha

### Instalação

```bash
# Clone o repositório
git clone https://github.com/PauloLimafps/PBIC.git
cd PBIC

# Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
```

### Configuração dos Secrets

Crie o arquivo `.streamlit/secrets.toml` com suas credenciais:

```toml
admin_users = ["admin", "taciana"]

[google_sheets]
spreadsheet_id = "SUA_SPREADSHEET_ID"

[google_sheets.credentials]
type = "service_account"
project_id = "seu-projeto"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "sua-conta@projeto.iam.gserviceaccount.com"
client_id = "..."
# ... demais campos da service account
```

### Execução

```bash
streamlit run app.py
```

Acesse: `http://localhost:8501`

---

## ☁️ Deploy no Streamlit Cloud

1. Faça fork/push do repositório para o GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io) e conecte o repositório
3. Em **Settings → Secrets**, cole o conteúdo do seu `secrets.toml`
4. O arquivo `.streamlit/config.toml` já está no repositório e é lido automaticamente

> ⚠️ **Nunca faça commit do `secrets.toml`!** Ele está no `.gitignore` por padrão.

---

## 🗂️ Google Sheets — Estrutura

### Aba 1 — Avaliações
`user_key | estudante | email_original | avaliador | denomine | defina | descreva | de_contexto | delimite | declare | determine | observacoes_col | data_criacao`

### Aba 2 — Perfil Avaliadores
`usuario | nome_completo | formacao | idade | area_atuacao | sexo | pos_graduacao | pos_graduacao_area | mestrado | mestrado_area | tipo_uso_ia | experiencia_ia | data_cadastro`

---

## 🛠️ Tecnologias

- [Streamlit](https://streamlit.io/) — framework de interface web
- [gspread](https://docs.gspread.org/) — integração com Google Sheets
- [Google Auth](https://google-auth.readthedocs.io/) — autenticação via Service Account
- [Pandas](https://pandas.pydata.org/) — manipulação de dados

---

## 📄 Licença

Projeto acadêmico — PBIC · 2026
