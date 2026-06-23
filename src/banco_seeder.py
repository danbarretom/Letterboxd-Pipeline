import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
URL_BANCO = os.getenv("DATABASE_URL")

def popular_banco_tarantino():
    if not URL_BANCO:
        print("❌ DATABASE_URL ausente no .env")
        return

    # Uma seleção de reviews realistas com nuances de sentimentos, sarcasmo e tópicos variados
    dados_tarantino = [
        ('Pulp Fiction', 'cinfilo_90', '★★★★★', 'Uma obra-prima absoluta do cinema modernista. Os diálogos casuais entre Vincent e Jules são espetaculares e o roteiro não-linear dita o ritmo perfeito do filme.'),
        ('Pulp Fiction', 'john_doe', '★★', 'Sinceramente? Superestimado. É apenas violência gratuita disfarçada de filme intelectual. O roteiro se arrasta por mais de duas horas.'),
        ('Kill Bill: Vol. 1', 'nana_filmes', '★★★★½', 'A estética visual desse filme é inacreditável. A coreografia da luta contra os 88 Loucos combina perfeitamente com a trilha sonora de pegada ocidental e anime.'),
        ('Kill Bill: Vol. 1', 'sarcastic_critic', '★★★', 'Ah, claro, porque decepar membros e jorrar sangue cenográfico é exatamente a definição de alta arte cinematográfica. Vale pelo estilo, mas a história é rasa igual a um pires.'),
        ('Django Unchained', 'marcos_v', '★★★★★', 'Christoph Waltz e Jamie Foxx entregam atuações dignas de Oscar. A direção de arte consegue recriar um período histórico tenso com uma acidez cirúrgica.'),
        ('Django Unchained', 'hater_tarantino', '★½', 'O ritmo do terceiro ato decai absurdamente depois que mudam de cenário. Tarantino não sabe a hora de encerrar seus filmes e se perde no próprio ego e no excesso de som alto.'),
        ('Bastardos Inglórios', 'clara_cinema', '★★★★★', 'A sequência de abertura na fazenda de leite é uma das coisas mais tensas já filmadas na história. A atuação do Hans Landa é impecável, você sente medo através da tela.'),
        ('Bastardos Inglórios', 'ironico_sempre', '★★★★', 'Amei como o Tarantino simplesmente decidiu reescrever a Segunda Guerra Mundial porque sim. O roteiro é pura fanfic histórica, mas a direção é tão boa que você aceita a mentira sorrindo.'),
        ('Era uma Vez em... Hollywood', 'thiago_art', '★★★½', 'É uma carta de amor à Hollywood dos anos 60. A fotografia e o figurino são impecáveis, mas admito que quem não conhece a história real da seita Manson vai achar o filme incrivelmente lento e sem rumo.')
    ]

    try:
        print("🔌 Conectando ao Supabase para semear dados...")
        conexao = psycopg2.connect(URL_BANCO)
        cursor = conexao.cursor()

        query = "INSERT INTO reviews_raw (filme, usuario, nota, review) VALUES (%s, %s, %s, %s);"
        cursor.executemany(query, dados_tarantino)

        conexao.commit()
        cursor.close()
        conexao.close()
        print(f"🎉 Sucesso! {len(dados_tarantino)} reviews estratégicas foram injetadas na tabela 'reviews_raw'.")

    except Exception as e:
        print(f"❌ Erro ao popular o banco: {e}")

if __name__ == "__main__":
    popular_banco_tarantino()