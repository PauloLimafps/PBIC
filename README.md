# Sistema de Avaliação de Prompts — PBIC

Aplicação web desenvolvida com **Streamlit** para avaliação de interações de estudantes com ferramentas de Inteligência Artificial. Os avaliadores analisam os prompts submetidos pelos alunos com base nos **7 Ds de um bom prompt**.

---

## Funcionalidades

- **Acesso sem senha** — qualquer avaliador cria seu próprio usuário pelo link do app
- **Cadastro de perfil na primeira vez** — dados pessoais, formação e experiência com IA
- **Distribuição sequencial de estudantes** — grupos de 10 por ordem de cadastro, com rotação circular
- **Guia dos 7 Ds** — painel explicativo colapsável no topo da tela de avaliação
- **Avaliação por 7 pilares** — critérios baseados no framework de prompts pedagógicos
- **Persistência no Google Sheets** — avaliações e perfis salvos em tempo real
- **Exportação CSV** — disponível para `admin` e `taciana`

---

## Estrutura do Projeto

```
PBIC/
├── app.py                  # Aplicativo principal Streamlit
├── google_sheets.py        # Integração com Google Sheets (perfis + avaliações)
├── conversations.json      # Base de interações dos estudantes
├── requirements.txt        # Dependências Python
├── .streamlit/
│   ├── config.toml         # Configurações do servidor (fix HTTPS)
│   └── secrets.toml        # Credenciais — NÃO vai ao GitHub
└── .gitignore
```

---

## Fluxo de Acesso

```
Acessa o app → digita nome de usuário (sem senha)
        ↓
┌─────────────────────┬──────────────────────────┐
│  Usuário NOVO       │  Usuário EXISTENTE        │
│  → Formulário de    │  → Vai direto para        │
│    perfil (1x só)   │    o app de avaliação     │
└─────────────────────┴──────────────────────────┘
```

| Usuário | Visibilidade |
|---------|-------------|
| `admin` | Todos os estudantes + exportar CSV |
| `taciana` | Todos os estudantes + exportar CSV |
| Qualquer outro | Grupo fixo de 10 estudantes (por ordem de cadastro) |

---

## Distribuição de Estudantes

Grupos de **10 estudantes** atribuídos sequencialmente pela **ordem de cadastro**:

| Cadastro | Estudantes |
|----------|-----------|
| 1º usuário | 1 – 10 |
| 2º usuário | 11 – 20 |
| 3º usuário | 21 – 30 |
| ... | ... |
| Quando os grupos acabam | Recomeça do grupo 1 (rotação circular) |

O grupo é fixo por sessão (cacheado) — o mesmo usuário sempre vê os mesmos estudantes.

---

## Formulário de Perfil (preenchido uma única vez)

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

## Os 7 Ds de um Bom Prompt

Exibidos em painel colapsável no topo da tela de avaliação.

| # | Pilar | O que avaliar |
|---|-------|--------------|
| 1 | **Denominar uma Persona** | Atribuiu papel/identidade à IA? |
| 2 | **Definir uma Tarefa** | Deixou claro o que a IA deve fazer? |
| 3 | **Descrever as Etapas** | Indicou o passo a passo? |
| 4 | **Dar Contexto** | Forneceu informações de fundo? |
| 5 | **Delimitar Restrições** | Indicou o que a IA não deve fazer? |
| 6 | **Declarar o Objetivo** | Explicou por que precisa da resposta? |
| 7 | **Determinar a Saída** | Especificou o formato de resposta? |

Opções de avaliação: **Atendeu** / **Parcialmente** / **Não Atendeu**

---

## Rodando Localmente

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

Crie `.streamlit/secrets.toml` com suas credenciais do Google Sheets:

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
```

```bash
streamlit run app.py
```

---

## Deploy no Streamlit Cloud

1. Faça push do repositório para o GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io) e conecte o repositório
3. Em **Settings → Secrets**, cole o conteúdo do seu `secrets.toml`
4. O `config.toml` já está no repositório e é lido automaticamente (corrige erro de HTTPS)

> **Nunca faça commit do `secrets.toml`!** Ele está no `.gitignore` por padrão.

---

## Google Sheets — Estrutura

**Aba 1 — Avaliações**
`user_key | estudante | email_original | avaliador | denomine | defina | descreva | de_contexto | delimite | declare | determine | observacoes_col | data_criacao`

**Aba 2 — Perfil Avaliadores**
`usuario | nome_completo | formacao | idade | area_atuacao | sexo | pos_graduacao | pos_graduacao_area | mestrado | mestrado_area | tipo_uso_ia | experiencia_ia | data_cadastro`

---

## Tecnologias

- [Streamlit](https://streamlit.io/)
- [gspread](https://docs.gspread.org/)
- [Google Auth](https://google-auth.readthedocs.io/)
- [Pandas](https://pandas.pydata.org/)

---

*Projeto acadêmico — PBIC · 2026*
