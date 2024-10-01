import tkinter as tk
import requests
import json


class ConfigLancamento:
    """Classe para configurar o lançamento da certidão carcerária."""

    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)  # Ajuste de margem esquerda consistente

        self.label_lancamento = tk.Label(self.frame, text="Certidão Carcerária:", width=0, anchor="e")
        self.label_lancamento.grid(row=0, column=0, sticky="ne", padx=(10, 5), pady=(10, 2))  # Reduzir padx para 10

        # URL do arquivo JSON na nuvem
        url_json = ("https://github.com/A-Assuncao/auto-saida-temporaria-canaime/releases/latest/download/lancamentos"
                    ".json")

        # Tenta carregar o texto de lançamento
        try:
            response = requests.get(url_json)
            response.raise_for_status()
            data = response.json()
            texto_exemplo = data.get('lancamento', "")
        except requests.RequestException as e:
            tk.messagebox.showerror("Erro", f"Não foi possível carregar o lançamento.\n{e}")
            texto_exemplo = ""

        width = 70  # Largura fixa para todas as caixas de texto

        self.lancamento_text = tk.Text(self.frame, wrap='word', height=10, width=width)
        self.lancamento_text.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=(10, 2))  # Reduzir padx para 10
        self.lancamento_text.insert(tk.END, texto_exemplo)
        self.highlight_placeholders(self.lancamento_text)

        # Permitir ajuste dinâmico de altura com base no conteúdo
        self.lancamento_text.bind("<KeyRelease>", lambda event, widget=self.lancamento_text: self.adjust_height(widget))

    def highlight_placeholders(self, text_widget):
        """Destaca e torna imutáveis os placeholders nas entradas de texto."""
        start_idx = text_widget.search("{", "1.0", tk.END)
        while start_idx:
            end_idx = text_widget.search("}", start_idx, tk.END)
            if not end_idx:
                break
            text_widget.tag_add("highlight", start_idx, f"{end_idx}+1c")
            text_widget.tag_config("highlight", foreground="red", font=("Helvetica", 10, "bold"))
            text_widget.tag_configure("immutable", background="lightgrey")
            text_widget.tag_add("immutable", start_idx, f"{end_idx}+1c")
            text_widget.tag_bind("immutable", "<KeyPress>", lambda e: "break")
            start_idx = text_widget.search("{", end_idx, tk.END)

    def adjust_height(self, widget):
        """Ajusta a altura do widget de texto com base no conteúdo."""
        num_lines = int(widget.index('end-1c').split('.')[0])
        widget.config(height=num_lines)

    def get_lancamento(self):
        """Retorna o texto de lançamento editado."""
        lancamento = self.lancamento_text.get("1.0", tk.END).strip()
        return lancamento
