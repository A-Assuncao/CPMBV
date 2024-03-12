import os
import getpass
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from playwright.sync_api import Playwright, sync_playwright

# Variáveis
ficha = 'https://canaime.com.br/sgp2rr/areas/unidades/Ficha_Menu.php?id_cad_preso='
cadastrar_portaria = 'https://canaime.com.br/sgp2rr/areas/unidades/Portaria_CAD_autorizar.php?id_cad_preso='
ler_portaria = 'https://canaime.com.br/sgp2rr/areas/unidades/Portaria_LER.php?id_cad_preso='
imprimir_portaria = 'https//canaime.com.br/sgp2rr/areas/impressoes/UND_Portaria.php?id_portaria='
historico = 'https://canaime.com.br/sgp2rr/areas/unidades/HistCar_LER.php?id_cad_preso='
data_inicio = '23/03/2024'
data_final = '29/03/2024'
dia_inicio = data_inicio[:2]
perfil = '/data/.st'
url_login_canaime = 'https://canaime.com.br/sgp2rr/login/login_principal.php'

artigos = {
    "1": f"Art. 1º - LIBERAR o reeducando do Regime Semiaberto, no período de {data_inicio} a {data_final} (07 dias), "
         "para o gozo da SAÍDA TEMPORÁRIA, em atenção a DECISÃO JUDICIAL existente nos autos de execução.",
    "2": "Art. 2º - A Liberação foi concedida em cumprimento a DECISÃO JUDICIAL advinda do Juiz de Direito da "
         f"Vara de Execuções Penais. Sendo DEFERIDA a Saída Temporária no período de {data_inicio} a {data_final} (07 "
         "dias) - conforme estabelecido na Portaria nº 06 de 23/11/2023 – publicado no Diário de Justiça "
         "Eletrônico – Ano XXVI / Edição 7506.",
    "3": "Art. 3º - O Reeducando declara ciência dos seus deveres e de sua condição, em especial a "
         "obrigatoriedade de:\n§1°. Fornecer comprovante do endereço onde poderá ser encontrado durante o gozo "
         "do benefício, comunicando eventual alteração do endereço.\n§2°. Para usufruir de Saídas Temporárias em "
         "endereços situados em outras Comarcas, o sentenciado deverá apresentar requerimento ao Juízo da Vara "
         "de Execução Penal, nos autos do respectivo Processo de Execução, em tempo hábil.\n§3°. Deverá o "
         "reeducando recolher-se diariamente à sua residência até as 20h00, podendo, durante o dia, "
         "a partir das 07h00, transitar, sem escolta, no território da comarca de Boa Vista, ou da cidade em "
         "que foi autorizado a usufruir o benefício;\n§4° Não praticar fato definido como crime;\n§5° Não "
         "praticar falta disciplinar de natureza grave;\n§6° Portar documentos de identificação e prestar "
         "esclarecimentos as autoridades sempre que requerido;\n§7º Proibição de frequentar bares, "
         "boates e estabelecimentos similares.",
    "4": "Art. 4º - O direito de usufruir o benefício da Saída Temporária independe de nova decisão àqueles que "
         "já possuam decisão judicial favorável referente a períodos anteriores, desde que o benefício não "
         "tenha sido revogado ou suspenso e mantenha o reeducando BOA conduta carcerária.",
    "5": f"Art. 5º - Deverá apresentar-se na CADEIA PÚBLICA MASCULINA DE BOA VISTA, até às 18h do dia {data_final}."
}


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def setup_browser_persistent(playwright: Playwright, sem_visual=True):
    if sem_visual:
        context = playwright.chromium.launch_persistent_context(headless=True, timeout=300000,
                                                                user_data_dir=perfil, ignore_https_errors=True)
    else:
        context = playwright.chromium.launch_persistent_context(headless=False, timeout=300000,
                                                                user_data_dir=perfil, ignore_https_errors=True)

    return context, context.new_page()


def login_canaime(p, sem_visual=True):
    msg_locator_logado = 'SIGP Canaimé 2.0. Todos os direitos reservados'
    print('Você precisará digitar seu usuário e senha do Canaimé. Os dados não serão gravados.')
    nome_usuario = input('Digite seu login: ')
    senha = input('Digite sua senha: ')
    # senha = getpass.getpass('Digite sua senha: ')

    context, page = setup_browser_persistent(p, sem_visual=sem_visual)
    page.goto(url_login_canaime, timeout=0)
    page.locator("input[name=\"usuario\"]").click()
    page.locator("input[name=\"usuario\"]").fill(nome_usuario)
    page.locator("input[name=\"usuario\"]").press("Tab")
    page.locator("input[name=\"senha\"]").fill(senha)
    page.locator("input[name=\"senha\"]").press("Enter")
    try:
        if msg_locator_logado in page.locator(".titulo").text_content():
            print('Login efetuado com sucesso')
    except Exception as e:
        page.close()
        print(f'Ocorreu um erro {e}')
        print('Usuário ou senha inválidos')
        exit()
    return page


def main(sem_visual=True, teste=False):
    Tk().withdraw()
    print('Selecione o arquivo Excel na janela que abrirá em seguida')
    arquivo_path = askopenfilename(title="Selecione o arquivo Excel")

    if teste:
        df = pd.read_excel(arquivo_path, nrows=1)
    else:
        df = pd.read_excel(arquivo_path)

    cdg = df['ID'].tolist()
    qtd = len(cdg)
    erros_st = []

    with sync_playwright() as p:
        clear_screen()
        page = login_canaime(p, sem_visual=sem_visual)
        try:
            clear_screen()
            print(f'Iniciando o processo de cadastro de portarias para {qtd} presos')
            for i, item in enumerate(cdg):
                clear_screen()
                texto = f"{ficha}{str(item)}"
                print(f'Iniciando o processo para o preso {item}')
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

                #     # imprimir portaria
                #     page.goto(imprimir_portaria + str(n_portaria))
                #     page.pdf(path=fr"data\{cela[i]}-{preso[i]}.pdf",
                #              format="A4", margin=dict(top="2cm", left="2cm", right="2cm", bottom="2cm"))

                # lançar certidão carcerária
                print(f'Portaria cadastrada para o preso {item}, realizando lançamento no histórico...')
                lancamento_certidao = (f"Foi devidamente autorizado pela Direção da CPBV - conforme Portaria "
                                       f"Nº {n_portaria}/2023/GAB/SAI/CPBV - a usufruir do benefício de SAÍDA "
                                       f"TEMPORÁRIA, sendo LIBERADO da unidade em {data_inicio} com determinação "
                                       f"de retorno até às 18h do dia {data_final}.")
                page.goto(historico + str(item))
                page.get_by_role("link", name="Cadastrar histórico carcerário").click()
                page.locator("#data").click()
                page.locator("#data").fill(data_inicio)
                page.locator("textarea[name=\"histcarc\"]").click()
                page.locator("textarea[name=\"histcarc\"]").fill(lancamento_certidao)
                page.get_by_role("button", name="CADASTRAR").click()
                print(f'Histórico de {item} lançado, faltam apenas {qtd - i - 1}!')
                print(texto)
        except Exception as e:
            erros_st.append([item, e, ficha + str(item)])

        erros_st = pd.DataFrame(erros_st, columns=["Código", "Erro", "Ficha"])
        erros_st.to_excel('data/Erros_ST.xlsx', index=False)
        num_erros = len(erros_st)
        erro_msg = f'Foi encontrado {num_erros} erro' if num_erros == 1 else f'Foram encontrados {num_erros} erros'
        print(erro_msg)

        if teste:
            print("Teste finalizado. Deseja apagar os dados do teste? Se sim, digite 'S'")
            if input("Digite: ").upper() == "S":
                # Apagar portaria
                page.goto(ler_portaria + str(item))
                name_locator = f"{n_portaria} {data_inicio} AUTORIZAR"
                page.get_by_role("row", name=name_locator).get_by_role("link").nth(2).click()
                page.get_by_role("button", name="EXCLUIR").click()

                # Apagar histórico
                page.goto(historico + str(item))
                page.get_by_role("link", name="Excluir histórico carcerário").first.click()
                page.get_by_role("button", name="EXCLUIR").click()


if __name__ == '__main__':
    navegador = input("Navegador:\n[1] Esconder\n[2] Mostrar\nDigite a Opção: ")
    if navegador == "1":
        main(sem_visual=True)
    elif navegador == "2":
        main(sem_visual=False)
    elif navegador == "2718":
        main(sem_visual=False, teste=True)
