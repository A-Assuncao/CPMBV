import tkinter as tk
import requests
import json

class ConfigArtigosPortaria:
    """Classe para configurar os artigos da portaria."""

    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)  # Ajuste de margem esquerda consistente

        # URL do arquivo JSON na nuvem
        url_json = ("https://github.com/A-Assuncao/auto-saida-temporaria-canaime/releases/latest/download/lancamentos"
                    ".json")

        # Tenta carregar os textos dos artigos
        try:
            response = requests.get(url_json)
            response.raise_for_status()
            data = response.json()
            artigos_textos = data.get('artigos', [])
        except requests.RequestException as e:
            tk.messagebox.showerror("Erro", f"Não foi possível carregar os artigos.\n{e}")
            artigos_textos = [""] * 5  # Cria uma lista vazia de artigos

        self.artigo_entries = []
        for i, texto in enumerate(artigos_textos, start=1):
            label = tk.Label(self.frame, text=f"Artigo {i}º:", width=15, anchor="e")
            label.grid(row=i, column=0, sticky="ne", padx=(10, 5), pady=(10, 2))  # Reduzir padx para 10

            # Definir altura dinâmica baseada no conteúdo, mantendo largura fixa
            num_lines = texto.count('\n') + texto.count('.') + 1
            height = max(5, num_lines)
            width = 70

            text_widget = tk.Text(self.frame, wrap='word', height=height, width=width)
            text_widget.grid(row=i, column=1, sticky="nsew", padx=(5, 10), pady=(10, 2))  # Reduzir padx para 10
            text_widget.insert(tk.END, texto)
            self.highlight_placeholders(text_widget)
            self.artigo_entries.append(text_widget)

            # text_widget.bind("<KeyRelease>", lambda event, widget=text_widget: self.adjust_height(widget))

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

    def get_artigos(self):
        """Retorna os artigos editados."""
        artigos = {str(i + 1): entry.get("1.0", tk.END).strip() for i, entry in enumerate(self.artigo_entries)}
        return artigos
