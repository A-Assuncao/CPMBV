# Automação de Saída Temporária

Este projeto é uma ferramenta de automação para gerenciar e registrar saídas temporárias de reeducandos usando o sistema Canaimé. O aplicativo interage com o sistema online, realiza o login, cadastra portarias e atualiza históricos de acordo com as decisões judiciais.

## Índice

1. [Requisitos](#requisitos)
2. [Instalação](#instalação)
3. [Estrutura do Projeto](#Estrutura-do-Projeto)
4. [Uso](#uso)
    - [Login no Sistema Canaimé](#login-no-sistema-canaimé)
    - [Configuração de Saída Temporária](#configuração-de-saída-temporária)
    - [Seleção do Arquivo Excel](#seleção-do-arquivo-excel)
    - [Processamento e Status](#processamento-e-status)
    - [Finalização](#finalização)
5. [Tratamento de Erros](#tratamento-de-erros)
6. [Contribuições](#contribuições)
7. [Licença](#licença)
8. [Agradecimentos](#agradecimentos)

## Requisitos

- [Python 3.8+](https://www.python.org/downloads/)
- [Pandas](https://pandas.pydata.org/) (`pip install pandas`)
- [Playwright](https://playwright.dev/python/docs/intro) (`pip install playwright`)
- Tkinter (normalmente incluído na instalação do Python)
- Outras bibliotecas listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
    ```bash
    git clone https://github.com/usuario/repo.git
    cd repo
    ```

2. Crie um ambiente virtual e ative-o:
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows use: venv\Scripts\activate
    ```

3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4. Instale e configure o Playwright:
    ```bash
    playwright install
    ```

## Estrutura do Projeto

```plaintext
auto-saida-temporaria-canaime/
│
├── main.py                            # Script principal para automação
├── config/
|   ├── config_artigos_portaria_st.py  # Configurações dos artigos da portaria
|   ├── config_lancamento_st.py        # Configurações do lançamentos na certidão
├── gui/
|   ├── interface_grafica.py           # Interface gráfica para coleta de dados
|   ├── login_canaime.py               # Interface gráfica para login
├── utils/
|   ├── __init__.py                    # Arquivo para tratar o diretório como pacote
|   ├── updater.py                     # Script para atualizar a aplicação
├── requirements.txt                   # Lista de dependências do Python
├── .gitignore                         # Arquivos e pastas ignorados pelo git
├── LICENSE                            # Licença de uso
└── README.md                          # Documentação do projeto
```

## Uso

### Login no Sistema Canaimé

- Ao iniciar o script `main.py`, a primeira janela que aparecerá será para inserir suas credenciais de login do sistema Canaimé.
- Insira seu nome de usuário e senha e clique em "Login".
- Uma mensagem de "Login efetuado com sucesso!" indicará que você foi autenticado com sucesso.

### Configuração de Saída Temporária

- Após o login, a interface gráfica principal abrirá.
- **Campos de Data**: Insira as datas de início e fim da saída temporária nos campos designados. As datas devem estar no formato `dd/mm/aaaa`.
- **Configuração dos Artigos**: Use a aba "Artigos" para editar os textos padrão dos artigos de portaria. Os campos `{data_inicio}`, `{data_final}`, e `{n_portaria}` serão automaticamente substituídos durante o processamento.
- **Lançamento da Certidão**: Na aba "Lançamentos", edite o texto da certidão carcerária. Este texto será usado para atualizar o histórico carcerário dos reeducandos.

### Seleção do Arquivo Excel

- Após configurar as datas e textos, uma janela solicitará que você selecione um arquivo Excel. Este arquivo deve conter uma lista dos IDs dos reeducandos que terão saídas temporárias.
- Uma vez selecionado, será exibida uma lista de colunas do Excel para que você escolha qual contém os IDs dos reeducandos.

### Processamento e Status

- Uma tela de status será exibida, mostrando o progresso do processamento de cada reeducando.
- O sistema fará o cadastro de portarias e lançamentos de certidões no histórico de cada reeducando.

### Finalização

- Após o processamento, os dados serão salvos em um arquivo Excel chamado `Saída Temporária.xlsx` e os documentos gerados serão armazenados na pasta designada.

## Tratamento de Erros

O sistema inclui tratamentos de exceções detalhados para capturar e registrar erros em um arquivo de log (`error_log.log`). Isso ajuda a identificar e corrigir problemas sem interromper o fluxo de processamento.

## Contribuições

Contribuições são bem-vindas! Por favor, siga as diretrizes de contribuição e mantenha um padrão consistente de codificação:

1. Faça um fork do projeto.

2. Crie uma branch para sua feature (`git checkout -b feature/SuaFeature`).

3. Commit suas mudanças (`git commit -m 'Adiciona a SuaFeature'`).

4. Faça um push para a branch (`git push origin feature/SuaFeature`).

5. Abra um Pull Request.


## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENÇA](LICENSE) para mais detalhes.

## Agradecimentos

Agradecemos a todos que contribuíram para o desenvolvimento deste projeto. Seu apoio é fundamental para o sucesso contínuo do software.
