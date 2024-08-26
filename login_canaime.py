import tkinter as tk
from threading import Thread
from playwright.sync_api import sync_playwright
import itertools
import time

# URL de login do sistema Canaimé
url_login_canaime = 'https://canaime.com.br/sgp2rr/login/login_principal.php'


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Canaimé")

        # Definir o tamanho da janela
        largura_janela = 300
        altura_janela = 225

        # Calcular a posição para centralizar a janela na tela
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()

        pos_x = (largura_tela - largura_janela) // 2
        pos_y = (altura_tela - altura_janela) // 2

        self.root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")  # Centralizar a janela

        # Configurar a janela para ficar sempre no topo
        self.root.attributes('-topmost', True)

        # Criar campo de entrada para usuário
        self.label_usuario = tk.Label(root, text="Usuário:", anchor='w')
        self.label_usuario.pack(pady=(10, 2))
        self.entry_usuario = tk.Entry(root)
        self.entry_usuario.pack(pady=(0, 10))

        # Criar campo de entrada para senha
        self.label_senha = tk.Label(root, text="Senha:", anchor='w')
        self.label_senha.pack(pady=(10, 2))
        self.entry_senha = tk.Entry(root, show="*")
        self.entry_senha.pack(pady=(0, 10))

        # Botão de login
        self.btn_login = tk.Button(root, text="Login", command=self.iniciar_login)
        self.btn_login.pack(pady=10)

        # Vincular o evento de pressionar Enter ao método de login
        self.root.bind('<Return>', self.on_enter)

        # Label de status para a animação de carregamento
        self.label_status = tk.Label(root, text="")
        self.label_status.pack(pady=10)

        # Variáveis para armazenar credenciais
        self.usuario = None
        self.senha = None

        # Animação da bolinha rodando
        self.animacao = None
        self.rodando = False

    def iniciar_login(self):
        # Desativa o botão de login e mostra o texto de carregamento
        self.btn_login.config(state=tk.DISABLED)
        self.label_status.config(text="Realizando login...")
        self.rodando = True

        # Iniciar animação de carregamento
        self.animacao = Thread(target=self.animar_bolinha)
        self.animacao.start()

        # Inicia o login em uma thread separada para não travar a interface
        thread = Thread(target=self.fazer_login)
        thread.start()


    def animar_bolinha(self):
        for frame in itertools.cycle(["◐", "◓", "◑", "◒"]):
            if not self.rodando:
                break
            self.root.after(0, self.label_status.config, {"text": f"Realizando login... {frame}"})
            time.sleep(0.2)


    def on_enter(self, event):
        """Método chamado quando a tecla Enter é pressionada."""
        self.iniciar_login()  # Chamar o método correto para iniciar o login


    def fazer_login(self):
        # Coletar os dados de login
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        if not usuario or not senha:
            self.rodando = False
            self.atualizar_interface(lambda: (
                self.label_status.config(text=""),
                self.btn_login.config(state=tk.NORMAL)
            ))
            return

        try:
            # Tentar fazer login com Playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)  # Modo headless pode ser False para ver o navegador
                context = browser.new_context()
                page = context.new_page()
                page.goto(url_login_canaime)

                page.locator("input[name=\"usuario\"]").fill(usuario)
                page.locator("input[name=\"senha\"]").fill(senha)
                page.locator("input[name=\"senha\"]").press("Enter")
                page.wait_for_timeout(5000)

                if page.locator('img').count() < 4:  # Suposição de que menos de 4 imagens indicam falha no login
                    self.rodando = False
                    self.atualizar_interface(lambda: (
                        self.label_status.config(text="Usuário ou senha inválidos."),
                        self.btn_login.config(state=tk.NORMAL)
                    ))
                else:
                    self.rodando = False
                    self.usuario = usuario
                    self.senha = senha
                    self.atualizar_interface(lambda: (
                        self.label_status.config(text="Login efetuado com sucesso!"),
                        self.root.after(1000, self.root.destroy)  # Fechar a janela após 1 segundo
                    ))

                browser.close()
        except Exception as e:
            self.rodando = False
            self.atualizar_interface(lambda: (
                self.label_status.config(text=f"Erro ao tentar login: {str(e)}"),
                self.btn_login.config(state=tk.NORMAL)
            ))
        finally:
            self.rodando = False
            self.atualizar_interface(lambda: self.btn_login.config(state=tk.NORMAL))

    def atualizar_interface(self, func):
        self.root.after(0, func)

    def get_credentials(self):
        return self.usuario, self.senha


# Função para executar a aplicação de login e retornar as credenciais
def executar_login():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
    return app.get_credentials()


if __name__ == "__main__":
    usuario, senha = executar_login()
    print(f"Usuário: {usuario}, Senha: {senha}")
