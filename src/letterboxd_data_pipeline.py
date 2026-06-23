from playwright.sync_api import sync_playwright
import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()
URL_BANCO = os.getenv("DATABASE_URL")

def salvar_no_banco(dados):
    if not dados:
        print("   ⚠️ Nenhuma avaliação processada.")
        return
    try:
        conexao = psycopg2.connect(URL_BANCO)
        cursor = conexao.cursor()
        query = "INSERT INTO reviews_raw (filme, usuario, nota, review) VALUES (%s, %s, %s, %s);"
        cursor.executemany(query, dados)
        conexao.commit()
        cursor.close()
        conexao.close()
        print(f"   💾 {len(dados)} reviews salvas no Supabase!")
    except Exception as e:
        print(f"   ❌ Erro no banco: {e}")

def executar_pipeline():
    if not URL_BANCO:
        print("❌ DATABASE_URL ausente no .env")
        return

    with sync_playwright() as p:
        print("🚀 Ligando o motor do navegador Firefox...")
        browser = p.firefox.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(60000)

        print("🔍 Acessando Letterboxd...")
        try:
            page.goto("https://letterboxd.com/director/quentin-tarantino/", wait_until="domcontentloaded")
            
            page.wait_for_selector("a[href^='/film/']", timeout=30000)
            time.sleep(2) 
            
            links = page.locator("a[href^='/film/']").all()
            filmes_unicos = {}

            for link in links:
                href = link.get_attribute("href")
                if href and len(href.split('/')) >= 3:
                    slug = href.split('/')[2]
                    
                    if slug and slug not in filmes_unicos and len(slug) > 2:
                        nome_formatado = slug.replace('-', ' ').title()
                        filmes_unicos[slug] = {
                            'Nome': nome_formatado,
                            'URL': f"https://letterboxd.com/film/{slug}/reviews/by/activity/"
                        }

            filmes = list(filmes_unicos.values())
            print(f"✅ {len(filmes)} filmes mapeados com sucesso! Iniciando extração...\n")

            # Vamos rodar o teste nos 3 primeiros filmes
            for filme in filmes[:3]:
                try:
                    print(f"   -> Tentando acessar: {filme['Nome']}")
                    # Retiramos o domcontentloaded para deixar a página de segurança carregar totalmente
                    page.goto(filme['URL'])
                    time.sleep(2)
                    
                    # SISTEMA ANTI-CLOUDFLARE COM AJUDA HUMANA
                    if "Just a moment" in page.title() or "Attention Required" in page.title():
                        print("      🛡️ Cloudflare bloqueou! Vá no navegador e clique na verificação...")
                        # O robô congela aqui por até 60 segundos esperando o título da página mudar
                        page.wait_for_function('document.title && !document.title.includes("Just a moment")', timeout=60000)
                        print("      🔓 Acesso liberado pelo Cloudflare! Retomando automação...")
                        time.sleep(3) # Pausa para a página real terminar de renderizar após o recarregamento
                    
                    print(f"      👀 Lendo a página: {page.title()}")
                    print("      ⏳ Aguardando os blocos de texto...")
                    
                    # Agora sim, com a página real carregada, procuramos as reviews
                    page.wait_for_selector("div.body-text", timeout=15000)

                    reviews_extraidas = []
                    itens_review = page.locator("div.body-text").all()
                    
                    print(f"      📊 Encontrados {len(itens_review)} blocos de texto. Extraindo...")

                    for item in itens_review:
                        try:
                            texto = item.inner_text().replace('\n', ' ').replace('\r', '')
                        except:
                            texto = "Sem texto"

                        if texto and texto != "Sem texto" and len(texto) > 10:
                            reviews_extraidas.append((filme['Nome'], "Usuário Letterboxd", "Nota no Site", texto))

                    salvar_no_banco(reviews_extraidas)
                    time.sleep(3)

                except Exception as erro_filme:
                    print(f"   ⚠️ Falha ao raspar {filme['Nome']}: {erro_filme}\n")
                    continue

        except Exception as e:
            print(f"\n❌ Erro crítico no pipeline: {e}")
        
        finally:
            print("\nFechando o navegador...")
            browser.close()
            print("🎉 Pipeline Playwright concluído!")

if __name__ == "__main__":
    executar_pipeline()