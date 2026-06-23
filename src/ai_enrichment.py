import psycopg2
import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
URL_BANCO = os.getenv("DATABASE_URL")

# Inicializa o cliente oficial moderno
client = genai.Client()

def analisar_com_gemini(texto_review):
    if len(texto_review) < 15:
        return {"Sentimento": "Neutro", "Tema_Principal": "Geral", "Sarcasmo": False}

    prompt = f"""
    Você é um analista de dados especialista em cinema.
    Analise a seguinte review de usuário do site Letterboxd e extraia as métricas solicitadas.
    
    Review: "{texto_review}"
    
    Retorne OBRIGATORIAMENTE um objeto JSON com esta estrutura exata:
    {{
        "Sentimento": "Positivo", "Negativo" ou "Neutro",
        "Tema_Principal": "Roteiro", "Atuação", "Trilha Sonora", "Direção", "Efeitos", "Geral" ou "Ritmo",
        "Sarcasmo": true ou false
    }}
    """

    try:
        # Atualizado para o modelo estável do novo SDK
        resposta = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        
        dados_analise = json.loads(resposta.text)
        return dados_analise
    except Exception as e:
        print(f" ⚠️ Erro na API do Gemini: {e}")
        return None # Retorna None para indicar que a chamada falhou estruturalmente

def executar_enriquecimento():
    if not URL_BANCO:
        print("❌ DATABASE_URL ausente no .env")
        return

    try:
        conexao = psycopg2.connect(URL_BANCO)
        cursor = conexao.cursor()

        # Busca as reviews pendentes
        cursor.execute("SELECT id, review FROM reviews_raw WHERE processado_ia = FALSE LIMIT 20;")
        linhas_pendentes = cursor.fetchall()

        if not linhas_pendentes:
            print("✨ Nenhuma review pendente encontrada para processamento.")
            return

        print(f"🤖 Iniciando processamento de {len(linhas_pendentes)} reviews com o Gemini...")

        for id_review, texto in linhas_pendentes:
            print(f"   -> Analisando ID {id_review}...")
            resultado = analisar_com_gemini(texto)

            # Se a IA falhar, pulamos a inserção e NÃO marcamos como processada
            if resultado is None:
                print(f"   ⚠️ ID {id_review} pulado devido a falha na API. Será tentado novamente depois.")
                continue

            # Se deu certo, salva na tabela enriquecida
            cursor.execute("""
                INSERT INTO reviews_enriched (id_review, sentimento, tema_principal, sarcasmo)
                VALUES (%s, %s, %s, %s);
            """, (id_review, resultado["Sentimento"], resultado["Tema_Principal"], resultado["Sarcasmo"]))

            # Atualiza o status na tabela original
            cursor.execute("UPDATE reviews_raw SET processado_ia = TRUE WHERE id = %s;", (id_review,))
            conexao.commit()
            time.sleep(1)

        cursor.close()
        conexao.close()
        print("✅ Processamento do bloco finalizado!")

    except Exception as e:
        print(f"❌ Erro no pipeline de IA: {e}")

if __name__ == "__main__":
    executar_enriquecimento()