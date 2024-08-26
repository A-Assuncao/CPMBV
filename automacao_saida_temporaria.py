import logging
import os
import sys
import time
import traceback
import tkinter as tk
import tkinter.font as font
from tkinter import filedialog, messagebox

import pandas as pd
from playwright.sync_api import sync_playwright

import updater
from interface_grafica import rodar_interface
from login_canaime import executar_login

current_version = 'v0.0.2'  # Versão atual do aplicativo

# URLs e variáveis globais
ficha = 'https://canaime.com.br/sgp2rr/areas/unidades/Ficha_Menu.php?id_cad_preso='
cadastrar_portaria = 'https://canaime.com.br/sgp2rr/areas/unidades/Portaria_CAD_autorizar.php?id_cad_preso='
ler_portaria = 'https://canaime.com.br/sgp2rr/areas/unidades/Portaria_LER.php?id_cad_preso='
url_imprimir_portaria = 'https://canaime.com.br/sgp2rr/areas/impressoes/UND_Portaria.php?id_portaria='
historico = 'https://canaime.com.br/sgp2rr/areas/unidades/HistCar_LER.php?id_cad_preso='
url_login_canaime = 'https://canaime.com.br/sgp2rr/login/login_principal.php'


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def capture_error(erro, contexto=""):
    logging.basicConfig(filename='error_log.log', level=logging.ERROR,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    error_message = f'Ocorreu um erro: {str(erro)}'
    traceback_message = traceback.format_exc()
    contexto_message = f'Contexto do Erro: {contexto}'
    logging.error(f'{error_message}\n{contexto_message}\nTraceback:\n{traceback_message}')


def login_canaime(p, sem_visual=True, usuario=None, senha=None):
    browser = p.chromium.launch(headless=sem_visual)
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()
    page.goto(url_login_canaime, timeout=0)
    page.locator("input[name=\"usuario\"]").click()
    page.locator("input[name=\"usuario\"]").fill(usuario)
    page.locator("input[name=\"senha\"]").click()
    page.locator("input[name=\"senha\"]").fill(senha)
    page.locator("input[name=\"senha\"]").press("Enter")
    return page


def show_processing_screen(root):
    """Cria uma nova janela para exibir o status do processamento com fonte maior e centralização."""
    processing_screen = tk.Toplevel(root)
    processing_screen.title("Processando...")
    processing_screen.geometry("400x200")  # Ajuste do tamanho da janela
    processing_screen.transient(root)

    # Definir fonte maior para o texto de status
    fonte_grande = font.Font(size=14)

    status_label = tk.Label(
        processing_screen,
        text="",
        justify="center",  # Centralizar o texto na janela
        font=fonte_grande,  # Usar fonte maior
        wraplength=500  # Quebrar linha se o texto for muito longo
    )
    status_label.pack(fill="both", expand=True, padx=20, pady=20)

    return processing_screen, status_label


def generate_pdf(pagina, lista_portarias, folder="portarias"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    for portaria in lista_portarias:
        full_pdf_path = os.path.join(folder, str(portaria) + ".pdf")
        pagina.goto(url_imprimir_portaria + str(portaria))
        pagina.emulate_media(media='screen')
        pagina.pdf(path=full_pdf_path, format="A4",
                   margin={"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"})


def coletar_dados_interface():
    usuario, senha = executar_login()

    if not usuario or not senha:
        raise ValueError("Erro ao coletar usuário e senha.")

    dados = rodar_interface()

    if not dados:
        raise ValueError("Erro ao coletar os dados da interface gráfica.")

    data_inicio = dados["data_inicio"]
    data_final = dados["data_final"]
    artigos = dados["artigos"]
    lancamento_certidao = dados["lancamento_certidao"]

    dia_inicio, mes_inicio, ano_inicio = data_inicio.split('/')
    mes_inicio = str(int(mes_inicio))

    # Realizar substituições nos textos
    for key in artigos:
        artigos[key] = artigos[key].replace("{data_inicio}", data_inicio).replace("{data_final}", data_final)
    lancamento_certidao = (
        lancamento_certidao
        .replace("{data_inicio}", data_inicio)
        .replace("{data_final}", data_final)
        # A substituição do {n_portaria} será feita durante o processo, pois varia para cada preso
    )

    # Coletar caminho do arquivo Excel
    print('Selecione o arquivo Excel na janela que abrirá em seguida...')
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    arquivo_path = filedialog.askopenfilename(title="Selecione o Arquivo Excel da Saída Temporária")
    root.attributes('-topmost', False)
    root.destroy()

    if not arquivo_path:
        raise ValueError("Nenhum arquivo Excel foi selecionado.")

    df = pd.read_excel(arquivo_path)

    # Criar uma nova janela para selecionar a coluna
    root = tk.Tk()
    root.title("Seleção de Coluna")
    root.attributes('-topmost', True)

    # Variável para armazenar a coluna selecionada
    coluna_selecionada = tk.StringVar()
    coluna_selecionada.set(None)

    def confirmar_selecao():
        if coluna_selecionada.get() == 'None':
            messagebox.showwarning("Aviso", "Por favor, selecione a coluna que contém os códigos/ID's:.")
        else:
            root.quit()

    # Obter todas as colunas não vazias
    colunas = [col for col in df.columns if df[col].notna().any()]

    # Mostrar pergunta ao usuário
    label_instrucao = tk.Label(root, text="Selecione a Coluna onde se encontram os códigos/ID's dos reeducandos:")
    label_instrucao.pack(pady=10)

    # Mostrar opções de colunas para o usuário
    for col in colunas:
        tk.Radiobutton(root, text=col, variable=coluna_selecionada, value=col).pack(anchor=tk.W)

    btn_confirmar = tk.Button(root, text="Confirmar", command=confirmar_selecao)
    btn_confirmar.pack(pady=10)

    # Ajustar tamanho da janela baseado no número de opções
    altura_janela = 100 + len(colunas) * 30
    largura_janela = 400
    root.geometry(f"{largura_janela}x{altura_janela}")

    root.mainloop()

    if coluna_selecionada.get() == 'None':
        root.destroy()
        raise ValueError("Nenhuma coluna foi selecionada.")

    coluna_id = coluna_selecionada.get()
    root.destroy()

    # Usar a coluna selecionada pelo usuário para obter os IDs
    cdg = df[coluna_id].tolist()

    dados_coletados = [
        usuario,
        senha,
        data_inicio,
        data_final,
        artigos,
        lancamento_certidao,
        dia_inicio,
        mes_inicio,
        ano_inicio,
        cdg
    ]

    return dados_coletados


def main(sem_visual=True):
    (usuario, senha, data_inicio, data_final, artigos, lancamento_certidao,
     dia_inicio, mes_inicio, ano_inicio, cdg) = coletar_dados_interface()

    qtd = len(cdg)
    portarias = []

    # Mostrar tela de processamento
    root = tk.Tk()
    root.title("Status Lançamentos")
    processing_screen, status_label = show_processing_screen(root)

    with sync_playwright() as p:

        # Fazendo login
        page = login_canaime(p, sem_visual=sem_visual, usuario=usuario, senha=senha)

        for i, item in enumerate(cdg):
            try:
                status_label.config(text=f"Processando preso {item} ({i + 1}/{qtd})...")
                processing_screen.update()

                # Acessar página de cadastro de portaria
                try:
                    page.goto(cadastrar_portaria + str(item))
                except Exception as e:
                    status_label.config(text=f"Erro ao acessar página de portaria para {item}: {str(e)}")
                    processing_screen.update()
                    print(f"Erro ao acessar página de portaria para {item}: {str(e)}")
                    continue

                # Preencher data
                try:
                    page.locator("select[name=\"dia\"]").select_option(data_inicio[:2])
                    page.locator("select[name=\"mes\"]").select_option(data_inicio[3:5])
                    page.locator("select[name=\"ano\"]").select_option(data_inicio[6:])
                except Exception as e:
                    status_label.config(text=f"Erro ao preencher data para {item}: {str(e)}")
                    processing_screen.update()
                    print(f"Erro ao preencher data para {item}: {str(e)}")
                    continue

                # Preencher artigos
                try:
                    for j, art_key in enumerate(['1', '2', '3', '4', '5'], start=1):
                        page.locator(f"textarea[name=\"paragrafo{j}\"]").click()
                        page.locator(f"textarea[name=\"paragrafo{j}\"]").press("Control+a")
                        page.locator(f"textarea[name=\"paragrafo{j}\"]").fill(artigos[str(art_key)])
                except Exception as e:
                    status_label.config(text=f"Erro ao preencher artigos para {item}: {str(e)}")
                    processing_screen.update()
                    print(f"Erro ao preencher artigos para {item}: {str(e)}")
                    continue

                # Cadastrar portaria
                try:
                    page.get_by_role("button", name="CADASTRAR").click()
                except Exception as e:
                    status_label.config(text=f"Erro ao cadastrar portaria para {item}: {str(e)}")
                    processing_screen.update()
                    print(f"Erro ao cadastrar portaria para {item}: {str(e)}")
                    continue

                # Ler o número da portaria
                try:
                    page.goto(ler_portaria + str(item))
                    n_portaria = page.locator('.titulobk:nth-child(1)').nth(0).text_content()
                    portarias.append(n_portaria)
                except Exception as e:
                    status_label.config(text=f"Erro ao ler número da portaria para {item}: {str(e)}")
                    processing_screen.update()
                    print(f"Erro ao ler número da portaria para {item}: {str(e)}")
                    continue

                # Substituir n_portaria no texto de lançamento
                lancamento_certidao_item = lancamento_certidao.replace("{n_portaria}", n_portaria)

                # Lançar certidão carcerária
                try:
                    page.goto(historico + str(item))
                    page.get_by_role("link", name="Cadastrar histórico carcerário").click()
                    page.locator("#data").click()
                    page.locator("#data").fill(data_inicio)
                    page.locator("textarea[name=\"histcarc\"]").click()
                    page.locator("textarea[name=\"histcarc\"]").fill(lancamento_certidao_item)
                    page.get_by_role("button", name="CADASTRAR").click()
                except Exception as e:
                    status_label.config(text=f"Erro ao lançar certidão carcerária para {item}: {str(e)}")
                    processing_screen.update()
                    print(f"Erro ao lançar certidão carcerária para {item}: {str(e)}")
                    continue

            except Exception as e:
                capture_error(e, contexto=f"Processando preso {item}")
                status_label.config(text=f"Erro inesperado para {item}: {str(e)}")
                processing_screen.update()
                print(f"Erro inesperado para {item}: {str(e)}")
                continue

        # Salvar resultados e gerar PDFs
        try:
            novo_df = pd.DataFrame({'ID': cdg, 'Portaria': portarias})
            novo_df.to_excel('Saída Temporária.xlsx', index=False)
            generate_pdf(page, portarias)
        except Exception as e:
            status_label.config(text=f"Erro ao salvar resultados: {str(e)}")
            processing_screen.update()
            print(f"Erro ao salvar resultados: {str(e)}")

        status_label.config(text="Processamento completo.")
        processing_screen.update()
        time.sleep(2)


if __name__ == '__main__':
    if updater.update_application(current_version):
        sys.exit(0)  # Exits the current application if an update is applied

    main(sem_visual=False)
