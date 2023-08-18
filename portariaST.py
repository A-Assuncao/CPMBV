import pandas as pd
from playwright.sync_api import sync_playwright
from credenciais import segredos

nome_usuario = segredos.get('NOME_USUARIO')
senha = segredos.get('SENHA')

# Variáveis
canaime = 'http://canaime.com.br/sgp2rr/'
ficha = 'http://canaime.com.br/sgp2rr/areas/unidades/Ficha_Menu.php?id_cad_preso='
cadastrar_portaria = 'http://canaime.com.br/sgp2rr/areas/unidades/Portaria_CAD_autorizar.php?id_cad_preso='
ler_portaria = 'http://canaime.com.br/sgp2rr/areas/unidades/Portaria_LER.php?id_cad_preso='
imprimir_portaria = 'http://canaime.com.br/sgp2rr/areas/impressoes/UND_Portaria.php?id_portaria='
historico = 'http://canaime.com.br/sgp2rr/areas/unidades/HistCar_LER.php?id_cad_preso='
data_ST = '13/05/2023'

art1 = 'Art. 1º: LIBERAR o reeducando do Regime Semiaberto, nos seguintes períodos: 13/05 a 19/05/2023, para o gozo ' \
       'da SAÍDA TEMPORÁRIA.'
art2 = 'Art. 2º: A liberação foi concedida em cumprimento à Portaria da Vara de Execução Penal nº 002, de 17 de ' \
       'fevereiro de 2023, previsto no art. 5º, Parágrafo Único.'
art3 = 'Art. 3º: O reeducando está CIENTE que não poderá mudar e nem se ausentar do Território da Comarca deste ' \
       'Juízo, sem prévia autorização judicial; deverá recolher-se a habitação até às 20hs; privar-se de frequentar ' \
       'bares, casas noturnas e semelhantes; não portar arma ou instrumento que possa ser utilizado como arma.'
art4 = 'Art. 4º: O reeducando está ciente de que deverá se apresentar neste Centro de Progressão Penitenciária no ' \
       'dia 20/05/2023, até às 19h30min.'
art5 = '''Art. 5º: Esta portaria entra em vigor nesta data. Comunique-se ao:
I- Ministério Público;
II- DESIPE.'''

df = pd.read_excel('data/ST.xlsx')
cdg = df['CÓDIGOS'].tolist()
preso = df['REEDUCANDO'].tolist()
cela = df['CELA'].tolist()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Login Sistema Canaimé
    page.goto(canaime)
    page.frame_locator("iframe[name=\"menu_esq\"]").frame_locator("text=<!--DWLayoutEmptyCell-->&nbsp;").locator(
        "input[name=\"usuario\"]").fill(nome_usuario)
    page.frame_locator("iframe[name=\"menu_esq\"]").frame_locator("text=<!--DWLayoutEmptyCell-->&nbsp;").locator(
        "input[name=\"senha\"]").fill(senha)
    page.frame_locator("iframe[name=\"menu_esq\"]").frame_locator("text=<!--DWLayoutEmptyCell-->&nbsp;").locator(
        "input[name=\"senha\"]").press("Enter")

    for i, item in enumerate(cdg):
        print(str(i) + ' ' + str(item) + ' ' + ficha + str(item))
        page.goto(cadastrar_portaria + str(item))
        page.locator("select[name=\"dia\"]").select_option("13")
        # Fazer a portaria:
        page.locator("textarea[name=\"paragrafo1\"]").click()
        page.locator("textarea[name=\"paragrafo1\"]").press("Control+a")
        page.locator("textarea[name=\"paragrafo1\"]").fill(art1)

        page.locator("textarea[name=\"paragrafo2\"]").click()
        page.locator("textarea[name=\"paragrafo2\"]").press("Control+a")
        page.locator("textarea[name=\"paragrafo2\"]").fill(art2)

        page.locator("textarea[name=\"paragrafo3\"]").click()
        page.locator("textarea[name=\"paragrafo3\"]").press("Control+a")
        page.locator("textarea[name=\"paragrafo3\"]").fill(art3)

        page.locator("textarea[name=\"paragrafo4\"]").click()
        page.locator("textarea[name=\"paragrafo4\"]").press("Control+a")
        page.locator("textarea[name=\"paragrafo4\"]").fill(art4)

        page.locator("textarea[name=\"paragrafo5\"]").click()
        page.locator("textarea[name=\"paragrafo5\"]").press("Control+a")
        page.locator("textarea[name=\"paragrafo5\"]").fill(art5)
        page.get_by_role("button", name="CADASTRAR").click()

        # Ler o número da portaria
        page.goto(ler_portaria + str(item))
        n_portaria = page.locator('.titulobk:nth-child(1)').nth(0).text_content()

        # imprimir portaria
        page.goto(imprimir_portaria + str(n_portaria))
        page.pdf(path=fr"\\Servidor-cpp\cpp 2018\2023\SAÍDA TEMPORÁRIA 2023\ST MAIO\Portarias\{cela[i]}-{preso[i]}.pdf",
                 format="A4", margin=dict(top="1cm", left="2cm", right="2cm", bottom="2cm"))

        # lançar certidão carcerária
        lancamento_certidao = f'Foi LIBERADO no período de 13/05 a 19/03/2023 para a SAÍDA TEMPORÁRIA. ' \
                              f'O reeducando está ciente de que deverá se apresentar nesta Unidade no dia ' \
                              f'20/05/2023, até às 19h30min, conforme PORTARIA nº {str(n_portaria)}/GAB/SAI/CPP.'
        page.goto(historico + str(item))
        page.get_by_role("link", name="Cadastrar histórico carcerário").click()
        page.locator("#data").click()
        page.locator("#data").fill(data_ST)
        page.locator("textarea[name=\"histcarc\"]").click()
        page.locator("textarea[name=\"histcarc\"]").fill(lancamento_certidao)
        page.get_by_role("button", name="CADASTRAR").click()
    page.close()
    browser.close()
