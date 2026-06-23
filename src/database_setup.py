import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url_banco = os.getenv("DATABASE_URL")

def iniciar_banco_postgres():
    if not url_banco:
        print("❌ ERRO: A variável DATABASE_URL não foi encontrada no arquivo .env.")
        return

    print("🔌 Conectando ao Supabase...")
    
    try:
        conexao = psycopg2.connect(url_banco)
        cursor = conexao.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews_raw (
            id SERIAL PRIMARY KEY,
            filme TEXT NOT NULL,
            usuario TEXT,
            nota TEXT,
            review TEXT,
            processado_ia BOOLEAN DEFAULT FALSE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews_enriched (
            id_review INTEGER REFERENCES reviews_raw(id) ON DELETE CASCADE,
            sentimento TEXT,
            tema_principal TEXT,
            sarcasmo BOOLEAN
        )
        ''')

        conexao.commit()
        cursor.close()
        conexao.close()
        print("✅ Sucesso! Tabelas 'reviews_raw' e 'reviews_enriched' criadas no Supabase.")

    except Exception as e:
        print(f"❌ Ocorreu um erro ao configurar o banco: {e}")

if __name__ == "__main__":
    iniciar_banco_postgres()