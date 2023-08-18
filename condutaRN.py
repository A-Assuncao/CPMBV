import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
from playwright.sync_api import sync_playwright
from credenciais import segredos
from listaCPP import criar_lista_cpp

nome_usuario = segredos.get('NOME_USUARIO')
senha = segredos.get('SENHA')

# Variáveis
canaime = 'http://canaime.com.br/sgp2rr/'
chamada = 'http://canaime.com.br/sgp2rr/areas/impressoes/UND_ChamadaFOTOS_todos2.php?id_und_prisional=CPP'
certidao = 'http://canaime.com.br/sgp2rr/areas/impressoes/UND_CertidaoCarceraria.php?id_cad_preso='

lista_cpp = criar_lista_cpp()
codigos = lista_cpp['Código'].tolist()
celas = lista_cpp['Cela'].tolist()
presos = lista_cpp['Preso'].tolist()
lista_conduta = pd.DataFrame(columns=['Código', 'Cela', 'Preso', 'Conduta'])

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
    for i, cdg in enumerate(codigos):
        link = certidao + cdg
        print(cdg + " " + link)
        page.goto(link)
        conduta = page.locator('tr:nth-child(11) .titulo12bk+ .titulobk').text_content()
        if conduta != 'BOA':
            lista_conduta.loc[len(lista_conduta)] = [int(cdg), celas[i], presos[i], conduta]

lista_conduta.sort_values(['Conduta', 'Preso'], inplace=True, ignore_index=True)
lista_conduta['Código'] = lista_conduta['Código'].apply(lambda x: '=HYPERLINK("%s", "%s")' % (certidao+str(x), str(x)))

# Crie um arquivo de trabalho excel usando openpyxl
wb = Workbook()
ws = wb.active

# Adicione o dataframe ao excel
for r in dataframe_to_rows(lista_conduta, index=False, header=True):
    ws.append(r)

# # Ajustar colunas de acordo com o conteúdo
# for column in ws.columns:
#     max_length = 0
#     column = [cell for cell in column]
#     for cell in column:
#         try:  # Necessário porque o valor pode ser de um tipo não string
#             if len(str(cell.value)) > max_length:
#                 max_length = len(cell.value)
#         except:
#             pass
#     adjusted_width = (max_length + 2)
#     ws.column_dimensions[column[0].column_letter].width = adjusted_width

# Salvar o arquivo Excel
wb.save("data/_Lista Conduta.xlsx")
