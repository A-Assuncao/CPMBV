import pandas as pd
from playwright.sync_api import sync_playwright

# Variáveis
url_login_canaime = 'http://canaime.com.br/sgp2rr/login/login_principal.php'
url_chamada_cpp = 'http://canaime.com.br/sgp2rr/areas/impressoes/UND_ChamadaFOTOS_todos2.php?id_und_prisional=CPP'


def login_canaime(page):
    # Login Sistema Canaimé
    print('Você precisará digitar seu usuário e senha do Canaimé.\n Os dados não serão gravados.')
    nome_usuario = input('Digite seu login: ')
    senha = input('Digite sua senha: ')

    page.goto(url_login_canaime, timeout=0)
    page.locator("input[name=\"usuario\"]").click()
    page.locator("input[name=\"usuario\"]").fill(nome_usuario)
    page.locator("input[name=\"usuario\"]").press("Tab")
    page.locator("input[name=\"senha\"]").fill(senha)
    page.locator("input[name=\"senha\"]").press("Enter")


def criar_lista_cpp():
    lista_cpp = pd.DataFrame(columns=['Código', 'Cela', 'Preso'])
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Chamar a função de login
        login_canaime(page)

        page.goto(url_chamada_cpp, timeout=0)
        page.locator('.titulobkSingCAPS >> nth=0')
        page.locator('.titulobkSingCAPS .titulo12bk >> nth=0')
        tudo = page.locator('.titulobkSingCAPS')
        nomes = page.locator('.titulobkSingCAPS .titulo12bk')
        count = tudo.count()
        for i in range(count):
            tudo_tratado = tudo.nth(i).text_content().replace(" ", "").strip()
            [codigo, _, _, _, ala] = tudo_tratado.split('\n')
            preso = nomes.nth(i).text_content().strip()
            lista_cpp.loc[len(lista_cpp)] = [codigo[2:], ala[-3:], preso]

        # Exclui presos com saída temporária
        try:
            df_saida_temporaria = pd.read_excel('data/ListaST.xlsx')
            df_saida_temporaria['Código'] = df_saida_temporaria['Código'].astype(str)
            df_saida_temporaria['Cela'] = df_saida_temporaria['Cela'].astype(str)
            df_saida_temporaria.sort_values(['Cela', 'Preso'], inplace=True, ignore_index=True)
            lista_cpp = pd.concat([lista_cpp, df_saida_temporaria])
            lista_cpp.sort_values(['Cela', 'Preso'], inplace=True, ignore_index=True)
            lista_cpp = lista_cpp.drop_duplicates(subset='Código', keep=False)
        except:
            pass
    return lista_cpp

if __name__ == '__main__':
    lista_cpp_geral = criar_lista_cpp()
    print(lista_cpp_geral)
