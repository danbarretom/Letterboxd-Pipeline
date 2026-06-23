import streamlit as st
import pandas as pd
import psycopg2
import os
import plotly.express as px
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()
URL_BANCO = os.getenv("DATABASE_URL")

# Configuração inicial da página do Streamlit
st.set_page_config(
    page_title="Tarantino AI Analytics",
    page_icon="🎬",
    layout="wide"
)

# Função para conectar ao Supabase e trazer os dados cruzados
@st.cache_data # Garante que o app não fique a sobrecarregar o banco a cada clique
def carregar_dados_do_banco():
    if not URL_BANCO:
        st.error("❌ DATABASE_URL não encontrada no .env")
        return pd.DataFrame()
    
    try:
        conexao = psycopg2.connect(URL_BANCO)
        
        # Query SQL para cruzar os dados brutos com a análise da IA
        query = """
            SELECT 
                r.filme, 
                r.usuario, 
                r.nota, 
                r.review, 
                e.sentimento, 
                e.tema_principal, 
                e.sarcasmo
            FROM reviews_raw r
            JOIN reviews_enriched e ON r.id = e.id_review;
        """
        
        df = pd.read_sql_query(query, conexao)
        conexao.close()
        return df
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao banco de dados: {e}")
        return pd.DataFrame()

# Carrega o DataFrame
df = carregar_dados_do_banco()

if df.empty:
    st.warning("⚠️ O banco de dados está vazio ou a conexão falhou.")
else:
    # --- TÍTULO PRINCIPAL ---
    st.title("🎬 Quentin Tarantino - Análise de Sentimento com IA")
    st.markdown("Este painel consome dados estruturados na nuvem através do **Supabase** e analisados pelo **Gemini (v2.5-flash)**.")
    st.divider()

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("Filtros do Projeto")
    filmes_disponiveis = ["Todos"] + list(df["filme"].unique())
    filme_selecionado = st.sidebar.selectbox("Selecione o Filme:", filmes_disponiveis)

    # Aplica o filtro de filme se não for "Todos"
    if filme_selecionado != "Todos":
        df_filtrado = df[df["filme"] == filme_selecionado]
    else:
        df_filtrado = df

    # --- KPI METRICS (INDICADORES RÁPIDOS) ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Reviews", len(df_filtrado))
    with col2:
        total_positivas = len(df_filtrado[df_filtrado["sentimento"] == "Positivo"])
        st.metric("Reviews Positivas", total_positivas)
    with col3:
        total_negativas = len(df_filtrado[df_filtrado["sentimento"] == "Negativo"])
        st.metric("Reviews Negativas", total_negativas)
    with col4:
        sarcasmo_detectado = len(df_filtrado[df_filtrado["sarcasmo"] == True])
        st.metric("Casos de Sarcasmo", sarcasmo_detectado)

    st.divider()

    # --- GRÁFICOS INCRÍVEIS ---
    col_grafico1, col_grafico2 = st.columns(2)

    with col_grafico1:
        st.subheader("🎭 Distribuição de Sentimentos")
        # Cria um gráfico de queijo/pizza interativo usando Plotly
        fig_sentimento = px.pie(
            df_filtrado, 
            names='sentimento', 
            color='sentimento',
            color_discrete_map={'Positivo': '#2ecc71', 'Negativo': '#e74c3c', 'Neutro': '#95a5a6'},
            hole=0.4
        )
        st.plotly_chart(fig_sentimento, use_container_width=True)

    with col_grafico2:
        st.subheader("🏷️ Temas Mais Abordados nas Críticas")
        # Conta a quantidade por tema principal
        df_temas = df_filtrado["tema_principal"].value_counts().reset_index()
        df_temas.columns = ["Tema", "Quantidade"]
        
        fig_temas = px.bar(
            df_temas, 
            x='Quantidade', 
            y='Tema', 
            orientation='h',
            color='Tema',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_temas, use_container_width=True)

    st.divider()

    # --- TABELA DE DADOS BRUTOS ---
    st.subheader("🔍 Inspecionar Avaliações e Decisões da IA")
    st.markdown("Abaixo pode ver o texto original que o utilizador escreveu e como o Gemini o classificou:")
    
    # Formata a tabela para exibição limpa
    st.dataframe(
        df_filtrado[["filme", "usuario", "nota", "review", "sentimento", "tema_principal", "sarcasmo"]],
        use_container_width=True
    )