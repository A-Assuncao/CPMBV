import os
import sys
import requests
import logging
import subprocess
import traceback
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from playwright.sync_api import sync_playwright

# Variáveis
ficha = 'https://canaime.com.br/sgp2rr/areas/unidades/Ficha_Menu.php?id_cad_preso='
cadastrar_portaria = 'https://canaime.com.br/sgp2rr/areas/unidades/Portaria_CAD_autorizar.php?id_cad_preso='
ler_portaria = 'https://canaime.com.br/sgp2rr/areas/unidades/Portaria_LER.php?id_cad_preso='
url_imprimir_portaria = 'https://canaime.com.br/sgp2rr/areas/impressoes/UND_Portaria.php?id_portaria='
historico = 'https://canaime.com.br/sgp2rr/areas/unidades/HistCar_LER.php?id_cad_preso='
data_inicio = '11/05/2024'
data_final = '17/05/2024'
dia_inicio, mes_inicio, ano_inicio = data_inicio.split('/')
mes_inicio = str(int(mes_inicio))  # Isso remove o zero à esquerda e mantém como string
url_login_canaime = 'https://canaime.com.br/sgp2rr/login/login_principal.php'

artigos = {
    "1": f"Art. 1º - LIBERAR o reeducando do Regime Semiaberto, no período de {data_inicio} a {data_final} (07 dias), "
         "para o gozo da SAÍDA TEMPORÁRIA, em atenção a DECISÃO JUDICIAL existente nos autos de execução.",
    "2": "Art. 2º - A Liberação foi concedida em cumprimento a DECISÃO JUDICIAL advinda do Juiz de Direito da "
         f"Vara de Execuções Penais. Sendo DEFERIDA a Saída Temporária no período de {data_inicio} a {data_final} (07 "
         "dias) - conforme estabelecido na Portaria nº 04 de 18/03/2024– publicado no Diário de Justiça Eletrônico – "
         "Ano XXVI / Edição 7582.",
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


def capture_error(erro):
    logging.basicConfig(filename='error_log.log', level=logging.ERROR,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    error_message = f'Ocorreu um erro: {str(erro)}'
    traceback_message = traceback.format_exc()
    logging.error(f'{error_message}\nTraceback:\n{traceback_message}')


def login_canaime(p, sem_visual=True):
    print('Você precisará digitar seu usuário e senha do Canaimé. Os dados não serão gravados.')
    nome_usuario = input('Digite seu login: ')
    senha = input('Digite sua senha: ')
    clear_screen()
    browser = p.chromium.launch(headless=sem_visual)
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()
    page.goto(url_login_canaime, timeout=0)
    page.locator("input[name=\"usuario\"]").click()
    page.locator("input[name=\"usuario\"]").fill(nome_usuario)
    page.locator("input[name=\"usuario\"]").press("Tab")
    page.locator("input[name=\"senha\"]").fill(senha)
    page.locator("input[name=\"senha\"]").press("Enter")
    page.wait_for_timeout(5000)
    try:
        if page.locator('img').count() < 4:
            print('Usuário ou senha inválidos')
            sys.exit(1)
        else:
            print('Login efetuado com sucesso!')
    except Exception as e1:
        capture_error(e1)
        sys.exit(1)

    return page


def print_pdf_files():
    response = input('Deseja imprimir as portarias? ("S" para confirmar): ').strip().lower()

    if response == "sim" or response == "s" or response == "yes" or response == "y":
        # URL do arquivo que você deseja baixar
        url = "https://www.print-conductor.com/files/printconductor-trial-setup.exe"

        # Nome do arquivo para salvar. Este será usado para construir o caminho completo
        filename = "printconductor-trial-setup.exe"

        # Constrói o caminho completo para salvar o arquivo
        save_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)

        try:
            # Faz o download do arquivo
            print(f"Baixando arquivo de {url}")
            response = requests.get(url)
            response.raise_for_status()  # Lança um erro para respostas não-sucedidas

            # Salva o arquivo no caminho especificado
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"Arquivo salvo em {save_path}")

            # Executa o arquivo baixado
            print("Iniciando o instalador...")
            subprocess.run(save_path, shell=True)

            # Caminho para o diretório 'portarias' relativo ao diretório atual do script
            folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portarias')

            # Abre o diretório no Windows Explorer
            subprocess.run(f'explorer "{folder_path}"', shell=True)

            # Apaga o arquivo baixado após a execução
            print("Apagando o instalador baixado...")
            os.remove(save_path)

        except requests.RequestException as e:
            print(f"Erro ao fazer o download: {e}")
        except Exception as e:
            print(f"Erro ao executar ou apagar o arquivo: {e}")


def generate_pdf(pagina, lista_portarias, folder="portarias"):
    # Verifica se a pasta existe, se não, cria
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Itera sobre a lista de portarias
    for portaria in lista_portarias:
        # Define o caminho do arquivo PDF para a portaria atual
        full_pdf_path = os.path.join(folder, str(portaria) + ".pdf")

        # Acessa a página para imprimir a portaria
        pagina.goto(url_imprimir_portaria + str(portaria))
        pagina.emulate_media(media='screen')

        # Gera o PDF com as margens especificadas e formato A4
        pagina.pdf(path=full_pdf_path, format="A4",
                   margin={"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"})


def main(sem_visual=True, teste=False):
    print('Selecione o arquivo Excel na janela que abrirá em seguida...')
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    arquivo_path = filedialog.askopenfilename(title="Selecione o Arquivo Excel da Saída Temporária")
    root.attributes('-topmost', False)
    root.destroy()

    if teste:
        df = pd.read_excel(arquivo_path, nrows=1)
    else:
        df = pd.read_excel(arquivo_path)

    cdg = df['ID'].tolist()
    qtd = len(cdg)
    portarias = []
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
                page.locator("select[name=\"mes\"]").select_option(mes_inicio)
                page.locator("select[name=\"ano\"]").select_option(ano_inicio)
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

                # Adicionar `n_portaria` à lista portarias
                portarias.append(n_portaria)

                # lançar certidão carcerária
                print(f'Portaria cadastrada para o preso {item}, realizando lançamento no histórico...')
                lancamento_certidao = (f"Foi devidamente autorizado pela Direção da CPBV - conforme Portaria "
                                       f"Nº {n_portaria}/2024/GAB/SAI/CPBV - a usufruir do benefício de SAÍDA "
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
        except Exception as e2:
            capture_error(e2)
            erros_st.append([item, e2, ficha + str(item)])

        # 3. Criar um novo DataFrame
        novo_df = pd.DataFrame({
            'ID': cdg,
            'Portaria': portarias
        })
        novo_df.to_excel('Saída Temporária.xlsx', index=False)
        generate_pdf(page, portarias)

    if len(erros_st) > 0:
        erros_st = pd.DataFrame(erros_st, columns=["Código", "Erro", "Ficha"])
        erros_st.to_excel('Erros_ST.xlsx', index=False)
        num_erros = len(erros_st)
        erro_msg = f'Foi encontrado {num_erros} erro' if num_erros == 1 else f'Foram encontrados {num_erros} erros'
        print(erro_msg)

    print_pdf_files()


if __name__ == '__main__':
    try:
        navegador = input("Navegador:\n[1] Esconder\n[2] Mostrar\nDigite a Opção: ")
        if navegador == "1":
            main(sem_visual=True)
        elif navegador == "2":
            main(sem_visual=False)
        elif navegador == "2718":
            main(sem_visual=False, teste=True)
    except Exception as e3:
        capture_error(e3)

    input('Pressione ENTER para sair...')
    sys.exit(0)
