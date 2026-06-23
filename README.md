# 🎬 Quentin Tarantino - Análise de Sentimento End-to-End com IA

Este projeto consiste numa infraestrutura completa de Engenharia de Dados orientada a objetos para coletar, armazenar, enriquecer com Inteligência Artificial e visualizar avaliações de filmes do realizador Quentin Tarantino.

O ecossistema integra bases de dados relacionais na nuvem, pipelines tolerantes a falhas usando o ecossistema mais recente da Google e um dashboard interativo para tomada de decisões analíticas.

## 🏗️ Arquitetura do Sistema

O pipeline de dados foi desenhado seguindo as melhores práticas de mercado:

1. **Infraestrutura como Código (IaC):** Criação automatizada de tabelas relacionais em PostgreSQL hospedado na nuvem via **Supabase**.
2. **Camada de Ingestão & Resiliência:** Scripts automatizados para alimentação do banco (`Data Seeding`) simulando volumetria de produção de críticas cinematográficas do Letterboxd.
3. **Orquestração & Enriquecimento:** Pipeline em Python integrado ao novo SDK da Google (`google-genai`) utilizando o modelo **Gemini 2.5 Flash** para extração estruturada de dados em formato JSON nativo (Análise de Sentimento, Tópicos e deteção de Sarcasmo).
4. **Camada de Visualização:** Interface Web reativa desenvolvida em **Streamlit** conectada diretamente ao banco de dados cloud.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Banco de Dados:** PostgreSQL (Supabase)
- **Engine de IA:** Google Gemini API (Model: `gemini-2.5-flash`)
- **Dashboard:** Streamlit, Plotly Express, Pandas
- **Conectores:** Psycopg2

## 🚀 Desafios Técnicos & Engenharia Reversa (Destaque Sênior)

Durante o desenvolvimento da camada de raspagem de dados web utilizando **Playwright (Firefox Core)**, o ecossistema enfrentou bloqueios avançados de impressão digital criptográfica (_Browser Fingerprinting_) gerados por firewalls de rede e sistemas de proteção global (Cloudflare) do site de origem.

**Decisão Arquitetural:** Em vez de comprometer o cronograma do projeto com contornos instáveis e de alto custo de manutenção, foi implementada uma estratégia robusta de **Data Seeding Controlado**. Foi desenvolvido um populador analítico para injetar dados realistas e nuances textuais complexas diretamente na base de dados, garantindo a integridade, a continuidade das esteiras de IA e a resiliência do pipeline.

## 📋 Como Executar o Projeto

### 1. Clonar o repositório

```bash
git clone [https://github.com/SEU_USUARIO/tarantino-ai-analytics.git](https://github.com/SEU_USUARIO/tarantino-ai-analytics.git)
cd tarantino-ai-analytics
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar as variáveis de ambiente

Crie um ficheiro `.env` na raiz do projeto:

```text
DATABASE_URL=postgresql://postgres.[ID_DO_PROJETO]:[SENHA]@[aws-0-sa-east-1.pooler.supabase.com:6543/postgres](https://aws-0-sa-east-1.pooler.supabase.com:6543/postgres)
GEMINI_API_KEY=sua_chave_da_api_aqui
```

### 4. Executar o fluxo em sequência

```bash
# 1. Configurar as tabelas na nuvem
python src/database_setup.py

# 2. Popular os dados brutos
python src/banco_seeder.py

# 3. Rodar a Inteligência Artificial para enriquecimento
python src/ai_enrichment.py

# 4. Levantar o Dashboard Web
streamlit run src/dashboard.py
```
