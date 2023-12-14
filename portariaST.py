import pandas as pd
from playwright.sync_api import sync_playwright
from main import login_canaime

# Variáveis
ficha = 'http://canaime.com.br/sgp2rr/areas/unidades/Ficha_Menu.php?id_cad_preso='
cadastrar_portaria = 'http://canaime.com.br/sgp2rr/areas/unidades/Portaria_CAD_autorizar.php?id_cad_preso='
ler_portaria = 'http://canaime.com.br/sgp2rr/areas/unidades/Portaria_LER.php?id_cad_preso='
imprimir_portaria = 'http://canaime.com.br/sgp2rr/areas/impressoes/UND_Portaria.php?id_portaria='
historico = 'http://canaime.com.br/sgp2rr/areas/unidades/HistCar_LER.php?id_cad_preso='
data_ST = '23/12/2023'
dia_inicio = data_ST[:2]
perfil = '/data/.st'

artigos = {
    "1": "Art. 1º - LIBERAR o reeducando do Regime Semiaberto, no período de 23/12/2023 a 29/12/2023 (07 dias), "
         "para o gozo da SAÍDA TEMPORÁRIA, em atenção a DECISÃO JUDICIAL existente nos autos de execução.",
    "2": "Art. 2º - A Liberação foi concedida em cumprimento a DECISÃO JUDICIAL advinda do Juiz de Direito da "
         "Vara de Execuções Penais. Sendo DEFERIDA a Saída Temporária no período de 23/12/2023 a 29/12/2023 (07 "
         "dias) - conforme estabelecido na Portaria nº 06 de 27/11/2023 – publicado no Diário de Justiça "
         "Eletrônico – Ano XXVI / Edição 7506.",
    "3": "Art. 3º - O Reeducando declara ciência dos seus deveres e de sua condição, em especial a "
         "obrigatoriedade de:\n§1°. Fornecer comprovante do endereço onde poderá ser encontrado durante o gozo "
         "do benefício, comunicando eventual alteração do endereço.\n§2°. Para usufruir de Saídas Temporárias em "
         "endereços situados em outras Comarcas, o sentenciado deverá apresentar requerimento ao Juízo da Vara "
         "de Execução Penal, nos autos do respectivo Processo de Execução, em tempo hábil.\n§3°. Deverá o "
         "reeducando recolher-se diariamente à sua residência até as 20h00, podendo, durante o dia, "
         "a partir das 07h00, transitar, sem escolta, no território da comarca de boa vista, ou da cidade em "
         "que foi autorizado a usufruir o benefício;\n§4° Não praticar fato definido como crime;\n§5° Não "
         "praticar falta disciplinar de natureza grave;\n§6° Portar documentos de identificação e prestar "
         "esclarecimentos as autoridades sempre que requerido;\n§7º Proibição de frequentar bares, "
         "boates e estabelecimentos similares.",
    "4": "Art. 4º - O direito de usufruir o benefício da Saída Temporária independe de nova decisão àqueles que "
         "já possuam decisão judicial favorável referente a períodos anteriores, desde que o benefício não "
         "tenha sido revogado ou suspenso e mantenha o reeducando BOA conduta carcerária.",
    "5": "Art. 5º - Deverá apresentar-se na CADEIA PÚBLICA MASCULINA DE BOA VISTA, até às 18h do dia 29/12/2023."
}
df = pd.read_excel('data/ST.xlsx')
cdg = df['ID'].tolist()
preso = df['REEDUCANDO'].tolist()
cela = df['ALA/CELA'].tolist()

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(headless=False, user_data_dir=perfil)
    page = context.new_page()
    # Login Sistema Canaimé
    login_canaime(page)

    for i, item in enumerate(cdg):
        print(str(i) + ' ' + str(item) + ' ' + ficha + str(item))
        page.goto(cadastrar_portaria + str(item))
        page.locator("select[name=\"dia\"]").select_option(dia_inicio)
        # Fazer a portaria:
        page.locator("textarea[name=\"paragrafo1\"]").click()
        page.locator("textarea[name=\"paragrafo1\"]").press("Control+a")
        page.locator("textarea[name=\"paragrafo1\"]").fill(artigos['1'])

        page.locator("textarea[name=\"paragrafo2\"]").click()
        page.locator("textarea[name=\"paragrafo2\"]").press("Control+a")
        page.locator("textarea[name=\"paragrafo2\"]").fill(artigos['2'])

        page.locator("textarea[name=\"paragrafo3\"]").click()
        page.locator("textarea[name=\"paragrafo3\"]").press("Control+a")
        page.locator("textarea[name=\"paragrafo3\"]").fill(artigos['3'])

        page.locator("textarea[name=\"paragrafo4\"]").click()
        page.locator("textarea[name=\"paragrafo4\"]").press("Control+a")
        page.locator("textarea[name=\"paragrafo4\"]").fill(artigos['4'])

        page.locator("textarea[name=\"paragrafo5\"]").click()
        page.locator("textarea[name=\"paragrafo5\"]").press("Control+a")
        page.locator("textarea[name=\"paragrafo5\"]").fill(artigos['5'])
        page.get_by_role("button", name="CADASTRAR").click()

        # Ler o número da portaria
        page.goto(ler_portaria + str(item))
        n_portaria = page.locator('.titulobk:nth-child(1)').nth(0).text_content()

        # imprimir portaria
        page.goto(imprimir_portaria + str(n_portaria))
        page.pdf(path=fr"data\{cela[i]}-{preso[i]}.pdf",
                 format="A4", margin=dict(top="2cm", left="2cm", right="2cm", bottom="2cm"))

        # lançar certidão carcerária
        lancamento_certidao = f'Foi LIBERADO no período de 23/12/2023 a 29/12/2023 para a SAÍDA TEMPORÁRIA. ' \
                              f'O reeducando está ciente de que deverá se apresentar nesta Unidade no dia ' \
                              f'29/12/2023, até às 18h00min, conforme PORTARIA nº {str(n_portaria)}/GAB/SAI/CPBV.'
        page.goto(historico + str(item))
        page.get_by_role("link", name="Cadastrar histórico carcerário").click()
        page.locator("#data").click()
        page.locator("#data").fill(data_ST)
        page.locator("textarea[name=\"histcarc\"]").click()
        page.locator("textarea[name=\"histcarc\"]").fill(lancamento_certidao)
        page.get_by_role("button", name="CADASTRAR").click()
    page.close()
    context.close()


# if __name__ == '__main__':
#     print('Fazer alguma coisa aqui')
