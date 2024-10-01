import logging
import os
import sys
import time
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox
import ctypes
import subprocess
import platform

import pandas as pd
from playwright.sync_api import sync_playwright

from utils.updater import update_application
from gui.interface_grafica import rodar_interface
from gui.login_canaime import executar_login

current_version = 'v0.0.2'  # Versão atual do aplicativo

# URLs e variáveis globais
ficha = 'https://canaime.com.br/sgp2rr/areas/unidades/Ficha_Menu.php?id_cad_preso='
cadastrar_portaria = 'https://canaime.com.br/sgp2rr/areas/unidades/Portaria_CAD_autorizar.php?id_cad_preso='
ler_portaria = 'https://canaime.com.br/sgp2rr/areas/unidades/Portaria_LER.php?id_cad_preso='
url_imprimir_portaria = 'https://canaime.com.br/sgp2rr/areas/impressoes/UND_Portaria.php?id_portaria='
historico = 'https://canaime.com.br/sgp2rr/areas/unidades/HistCar_LER.php?id_cad_preso='
url_login_canaime = 'https://canaime.com.br/sgp2rr/login/login_principal.php'


# Ativar logs detalhados
# os.environ['DEBUG'] = 'pw:api'


def hide_console():
    """Esconde a janela do console."""
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd != 0:
        ctypes.windll.user32.ShowWindow(hwnd, 0)  # 0 = Esconder a janela


def show_console():
    """Traz a janela do console para frente."""
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd != 0:
        ctypes.windll.user32.ShowWindow(hwnd, 1)  # 1 = Mostrar a janela (restaurar)
        ctypes.windll.user32.SetForegroundWindow(hwnd)  # Traz a janela para frente


def clear_console():
    """Limpa o console de acordo com o sistema operacional."""
    # Para sistemas Windows
    if os.name == 'nt':
        os.system('cls')
    # Para sistemas Unix/Linux/Mac
    else:
        os.system('clear')


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
    # Coleta dos dados iniciais (login, datas, artigos, lançamento)
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
    )

    # Loop para permitir que o usuário selecione um novo arquivo ou coluna
    while True:
        # Seleção do arquivo Excel
        arquivo_path = selecionar_arquivo_excel()
        if not arquivo_path:
            raise ValueError("Nenhum arquivo Excel foi selecionado.")

        try:
            df = pd.read_excel(arquivo_path)
            if df.empty:
                raise ValueError("O arquivo Excel selecionado está vazio.")
        except Exception as e:
            retry = messagebox.askretrycancel(
                "Erro ao carregar o arquivo",
                f"Não foi possível carregar o arquivo selecionado.\nErro: {e}\n\nDeseja tentar novamente?"
            )
            if not retry:
                raise ValueError("Operação cancelada pelo usuário.")
            else:
                continue  # Volta ao início do loop para selecionar um novo arquivo

        # Seleção da coluna com os IDs
        try:
            coluna_id = selecionar_coluna_id(df)
            if not coluna_id:
                raise ValueError("Nenhuma coluna foi selecionada.")
            cdg = df[coluna_id].tolist()
            break  # Sai do loop após seleção bem-sucedida
        except Exception as e:
            if str(e) == "Selecionar novo arquivo":
                continue  # Reinicia o loop para selecionar um novo arquivo
            else:
                raise e

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


def selecionar_arquivo_excel():
    """Função para selecionar o arquivo Excel."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    arquivo = filedialog.askopenfilename(
        title="Selecione o Arquivo Excel da Saída Temporária",
        filetypes=[("Arquivos Excel", "*.xlsx;*.xls")]
    )
    root.attributes('-topmost', False)
    root.destroy()
    return arquivo


def selecionar_coluna_id(df):
    """Função para selecionar a coluna que contém os IDs."""
    root = tk.Tk()
    root.title("Seleção de Coluna")
    root.attributes('-topmost', True)

    selecionar_novo_arquivo_flag = False  # Flag para indicar se o usuário deseja selecionar um novo arquivo

    coluna_selecionada = tk.StringVar()
    coluna_selecionada.set(None)

    def confirmar_selecao():
        if coluna_selecionada.get() == 'None':
            messagebox.showwarning("Aviso", "Por favor, selecione a coluna que contém os códigos/ID's.")
        else:
            root.quit()

    def selecionar_novo_arquivo():
        nonlocal selecionar_novo_arquivo_flag
        selecionar_novo_arquivo_flag = True
        root.quit()

    colunas = [col for col in df.columns if df[col].notna().any()]

    # Configurar o grid do root
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)

    # Label de instrução
    label_instrucao = tk.Label(
        root,
        text="Selecione a coluna onde se encontram os códigos/ID's dos reeducandos:",
        font=('Arial', 12)
    )
    label_instrucao.grid(row=0, column=0, padx=20, pady=(20, 10), sticky='w')

    # Frame para os RadioButtons
    frame_radios = tk.Frame(root)
    frame_radios.grid(row=1, column=0, padx=20, sticky='nw')

    # Adicionar uma scrollbar caso haja muitas colunas
    canvas = tk.Canvas(frame_radios)
    scrollbar = tk.Scrollbar(frame_radios, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for i, col in enumerate(colunas):
        tk.Radiobutton(
            scrollable_frame,
            text=col,
            variable=coluna_selecionada,
            value=col,
            font=('Arial', 12),
            anchor='w',
            justify='left'
        ).grid(row=i, column=0, sticky='w')

    # Frame para os botões
    frame_botoes = tk.Frame(root)
    frame_botoes.grid(row=2, column=0, pady=15)

    # Botões com mesmo tamanho
    btn_confirmar = tk.Button(
        frame_botoes,
        text="Continuar",
        command=confirmar_selecao,
        font=('Arial', 12),
        width=20  # Definir largura fixa
    )
    btn_confirmar.pack(side=tk.LEFT, padx=5)

    btn_novo_arquivo = tk.Button(
        frame_botoes,
        text="Selecionar Novo Arquivo",
        command=selecionar_novo_arquivo,
        font=('Arial', 12),
        width=20  # Definir largura fixa
    )
    btn_novo_arquivo.pack(side=tk.LEFT, padx=5)

    # Ajustar tamanho da janela
    largura_janela = 600  # Aumentar a largura da janela
    altura_janela = 400   # Aumentar a altura da janela
    root.geometry(f"{largura_janela}x{altura_janela}")

    # Centralizar a janela na tela
    root.update_idletasks()
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    pos_x = (largura_tela - largura_janela) // 2
    pos_y = (altura_tela - altura_janela) // 2
    root.geometry(f"+{pos_x}+{pos_y}")

    root.mainloop()

    if selecionar_novo_arquivo_flag:
        root.destroy()
        raise Exception("Selecionar novo arquivo")

    if coluna_selecionada.get() == 'None':
        root.destroy()
        return None

    coluna_id = coluna_selecionada.get()
    root.destroy()
    return coluna_id


def main(sem_visual=True):
    hide_console()
    (usuario, senha, data_inicio, data_final, artigos, lancamento_certidao,
     dia_inicio, mes_inicio, ano_inicio, cdg) = coletar_dados_interface()

    qtd = len(cdg)
    portarias = []
    errors = []

    with sync_playwright() as p:
        page = login_canaime(p, sem_visual=sem_visual, usuario=usuario, senha=senha)
        clear_console()
        show_console()

        for i, item in enumerate(cdg):
            print(f"({i + 1}/{qtd}) Processando preso {item}, restam {qtd - (i + 1)}...")
            try:
                # Navegar para a página de cadastro de portaria
                page.goto(cadastrar_portaria + str(item))
            except Exception as e:
                error_message = f"Erro ao acessar página de portaria para {item}: {str(e)}"
                print(error_message)
                errors.append({'ID': item, 'Erro': error_message})
                continue

            # Preencher data
            try:
                page.locator("select[name=\"dia\"]").select_option(data_inicio[:2])
                page.locator("select[name=\"mes\"]").select_option(mes_inicio)
                page.locator("select[name=\"ano\"]").select_option(data_inicio[6:])
            except Exception as e:
                error_message = f"Erro ao preencher data para {item}: {str(e)}"
                print(error_message)
                errors.append({'ID': item, 'Erro': error_message})
                continue

            # Preencher artigos
            try:
                for j, art_key in enumerate(['1', '2', '3', '4', '5'], start=1):
                    page.locator(f"textarea[name=\"paragrafo{j}\"]").click()
                    page.locator(f"textarea[name=\"paragrafo{j}\"]").press("Control+a")
                    page.locator(f"textarea[name=\"paragrafo{j}\"]").fill(artigos[str(art_key)])
            except Exception as e:
                error_message = f"Erro ao preencher artigos para {item}: {str(e)}"
                print(error_message)
                errors.append({'ID': item, 'Erro': error_message})
                continue

            # Cadastrar portaria
            try:
                page.get_by_role("button", name="CADASTRAR").click()
            except Exception as e:
                error_message = f"Erro ao cadastrar portaria para {item}: {str(e)}"
                print(error_message)
                errors.append({'ID': item, 'Erro': error_message})
                continue

            # Ler número da portaria
            try:
                page.goto(ler_portaria + str(item))
                n_portaria = page.locator('.titulobk:nth-child(1)').nth(0).text_content()
                portarias.append(n_portaria)
            except Exception as e:
                error_message = f"Erro ao ler número da portaria para {item}: {str(e)}"
                print(error_message)
                errors.append({'ID': item, 'Erro': error_message})
                continue

            # Preencher lançamento da certidão carcerária
            lancamento_certidao_item = lancamento_certidao.replace("{n_portaria}", n_portaria)
            try:
                page.goto(historico + str(item))
                page.get_by_role("link", name="Cadastrar histórico carcerário").click()
                page.locator("#data").click()
                page.locator("#data").fill(data_inicio)
                page.locator("textarea[name=\"histcarc\"]").click()
                page.locator("textarea[name=\"histcarc\"]").fill(lancamento_certidao_item)
                page.get_by_role("button", name="CADASTRAR").click()
            except Exception as e:
                error_message = f"Erro ao lançar certidão carcerária para {item}: {str(e)}"
                print(error_message)
                errors.append({'ID': item, 'Erro': error_message})
                continue

            time.sleep(1)

    # Após o loop principal
    if errors:
        print("Ocorreram erros durante o processamento.")
        # Perguntar ao usuário onde salvar o arquivo Excel com os erros
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx")],
                                                 title="Salvar lista de erros",
                                                 initialfile="Erros Lançamento ST.xlsx")

        if file_path:
            try:
                df_errors = pd.DataFrame(errors)
                df_errors.to_excel(file_path, index=False)
                print(f"Lista de erros salva em: {file_path}")
                # Abrir o arquivo Excel
                abrir_arquivo(file_path)
            except Exception as save_error:
                print(f"Erro ao salvar o arquivo de erros: {str(save_error)}")
        else:
            print("Salvamento da lista de erros cancelado pelo usuário.")
    else:
        print("Processamento concluído sem erros.")


def abrir_arquivo(caminho):
    """Abre o arquivo especificado no sistema operacional."""
    try:
        if platform.system() == "Windows":
            os.startfile(caminho)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", caminho])
        else:  # Linux e outros
            subprocess.call(["xdg-open", caminho])
    except Exception as e:
        print(f"Não foi possível abrir o arquivo: {str(e)}")


if __name__ == '__main__':
    if update_application(current_version):
        sys.exit(0)  # Exits the current application if an update is applied

    main(sem_visual=True)
