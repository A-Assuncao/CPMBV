import tkinter as tk
from tkinter import ttk, messagebox
from config.config_artigos_portaria_st import ConfigArtigosPortaria
from config.config_lancamento_st import ConfigLancamento
from datetime import datetime
import re


class InterfaceGrafica:
    """Classe para gerenciar a interface gráfica principal."""

    def __init__(self, root):
        self.root = root
        self.root.title("Configuração de Saída Temporária")
        self.dados_salvos = None  # Variável para armazenar os dados

        # Campos de data
        self.create_data_fields()

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)

        # Aba de configuração dos artigos
        artigos_frame = tk.Frame(notebook)
        self.artigos_config = ConfigArtigosPortaria(artigos_frame)
        notebook.add(artigos_frame, text="Artigos")

        # Aba de lançamento da certidão
        lancamento_frame = tk.Frame(notebook)
        self.lancamento_config = ConfigLancamento(lancamento_frame)
        notebook.add(lancamento_frame, text="Lançamentos")

        # Botão de salvar
        btn_salvar = tk.Button(self.root, text="Salvar e Continuar", command=self.salvar_dados)
        btn_salvar.pack(pady=20, padx=10, ipadx=20, ipady=5)  # Ajuste para largura e altura do botão

    def create_data_fields(self):
        """Cria os campos de entrada de data fora das abas."""
        data_frame = tk.Frame(self.root)
        data_frame.pack(pady=10)

        self.label_data_inicio = tk.Label(data_frame, text="Data de Início:")
        self.label_data_inicio.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_data_inicio = tk.Entry(data_frame, width=20)
        self.entry_data_inicio.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.set_placeholder_behavior(self.entry_data_inicio, "Dia da liberação...")
        self.entry_data_inicio.bind("<KeyRelease>", self.format_date)

        self.label_data_final = tk.Label(data_frame, text="Data Final:")
        self.label_data_final.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_data_final = tk.Entry(data_frame, width=20)
        self.entry_data_final.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.set_placeholder_behavior(self.entry_data_final, "Dia do retorno...")
        self.entry_data_final.bind("<KeyRelease>", self.format_date)

    def set_placeholder_behavior(self, entry, placeholder_text):
        """Configura o comportamento de placeholder para os campos de entrada."""

        def on_focus_in(event):
            if entry.get() == placeholder_text:
                entry.delete(0, tk.END)
                entry.config(fg='black')

        def on_focus_out(event):
            if entry.get() == '':
                entry.insert(0, placeholder_text)
                entry.config(fg='grey')

        entry.insert(0, placeholder_text)
        entry.config(fg='grey')
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def format_date(self, event):
        """Formata a entrada de data com barras (dd/mm/aaaa) e impede mais de 10 caracteres."""
        entry = event.widget
        text = entry.get().replace("/", "")  # Remover barras temporariamente

        # Impede mais de 8 caracteres numéricos
        if len(text) > 8:
            text = text[:8]

        # Formatação da data com barras
        if len(text) > 2:
            text = text[:2] + '/' + text[2:]
        if len(text) > 5:
            text = text[:5] + '/' + text[5:]

        # Insere o texto formatado, limitando a 10 caracteres
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def salvar_dados(self):
        """Salva os dados dos artigos e do lançamento."""
        data_inicio = self.entry_data_inicio.get()
        data_final = self.entry_data_final.get()

        if not self.is_valid_date(data_inicio) or not self.is_valid_date(data_final):
            messagebox.showerror("Erro de Validação", "Por favor, insira datas válidas no formato dd/mm/aaaa.")
            return

        data_inicio_dt = datetime.strptime(data_inicio, "%d/%m/%Y")
        data_final_dt = datetime.strptime(data_final, "%d/%m/%Y")

        if data_final_dt <= data_inicio_dt:
            messagebox.showerror("Erro de Validação", "A data final deve ser posterior à data de início.")
            return

        artigos = self.artigos_config.get_artigos()
        lancamento = self.lancamento_config.get_lancamento()

        self.dados_salvos = {
            "data_inicio": data_inicio,
            "data_final": data_final,
            "lancamento_certidao": lancamento,
            "artigos": artigos,
        }

        self.root.destroy()  # Fecha a janela e termina a aplicação

    def is_valid_date(self, date_text):
        """Valida se a data está no formato dd/mm/aaaa e se é uma data válida."""
        pattern = r"^\d{2}/\d{2}/\d{4}$"
        if not re.match(pattern, date_text):
            return False

        try:
            datetime.strptime(date_text, "%d/%m/%Y")
            return True
        except ValueError:
            return False


def rodar_interface():
    root = tk.Tk()
    root.title("Configuração de Saída Temporária")
    largura_janela, altura_janela = 750, 900
    pos_x = (root.winfo_screenwidth() - largura_janela) // 2
    pos_y = (root.winfo_screenheight() - altura_janela) // 2
    root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    app = InterfaceGrafica(root)
    root.mainloop()

    return app.dados_salvos  # Retorna os dados salvos


if __name__ == "__main__":
    dados = rodar_interface()
    print(dados)
