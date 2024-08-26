import tkinter as tk

class ConfigArtigosPortaria:
    """Classe para configurar os artigos da portaria."""

    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)  # Ajuste de margem esquerda consistente

        artigos_textos = [
            "Art. 1º - LIBERAR o reeducando do Regime Semiaberto, no período de {data_inicio} a {data_final} (07 "
            "dias), para o gozo da SAÍDA TEMPORÁRIA, em atenção a DECISÃO JUDICIAL existente nos autos de execução.",
            "Art. 2º - A Liberação foi concedida em cumprimento a DECISÃO JUDICIAL advinda do Juiz de Direito da Vara "
            "de Execuções Penais. Sendo DEFERIDA a Saída Temporária no período de {data_inicio} a {data_final} (07 "
            "dias) - conforme estabelecido na Portaria nº 04 de 18/03/2024– publicado no Diário de Justiça Eletrônico "
            "– Ano XXVI / Edição 7582.",
            "Art. 3º - O Reeducando declara ciência dos seus deveres e de sua condição, em especial a obrigatoriedade "
            "de:\n§1°. Fornecer comprovante do endereço onde poderá ser encontrado durante o gozo do benefício, "
            "comunicando eventual alteração do endereço.\n§2°. Para usufruir de Saídas Temporárias em endereços "
            "situados em outras Comarcas, o sentenciado deverá apresentar requerimento ao Juízo da Vara de Execução "
            "Penal, nos autos do respectivo Processo de Execução, em tempo hábil.\n§3°. Deverá o reeducando "
            "recolher-se diariamente à sua residência até as 20h00, podendo, durante o dia, a partir das 07h00, "
            "transitar, sem escolta, no território da comarca de Boa Vista, ou da cidade em que foi autorizado a "
            "usufruir o benefício;\n§4° Não praticar fato definido como crime;\n§5° Não praticar falta disciplinar de "
            "natureza grave;\n§6° Portar documentos de identificação e prestar esclarecimentos as autoridades sempre "
            "que requerido;\n§7º Proibição de frequentar bares, boates e estabelecimentos similares.",
            "Art. 4º - O direito de usufruir o benefício da Saída Temporária independe de nova decisão àqueles que já "
            "possuam decisão judicial favorável referente a períodos anteriores, desde que o benefício não tenha sido "
            "revogado ou suspenso e mantenha o reeducando BOA conduta carcerária.",
            "Art. 5º - Deverá apresentar-se na CADEIA PÚBLICA MASCULINA DE BOA VISTA, até às 18h do dia {data_final}."
        ]

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

            text_widget.bind("<KeyRelease>", lambda event, widget=text_widget: self.adjust_height(widget))

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
