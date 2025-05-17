# OCR com Gemini e Tkinter

Este projeto é uma aplicação desktop desenvolvida em Python com uma interface gráfica criada usando Tkinter. Ele permite ao usuário selecionar um arquivo de imagem, fornecer um prompt opcional e enviar a imagem para a API do Google Gemini para realizar a extração de texto (OCR).

## Telas da Aplicação

**Telas**
[Tela Principal]([https://t3rcio.com.br/assets/Tela__1__2025-05-16_23-12-11.png])
[Tela com Imagem e Resultado]([https://t3rcio.com.br/assets/Tela__2__2025-05-16_23-13-01.png])

## Funcionalidades

*   Interface gráfica amigável construída com Tkinter.
*   Seleção de arquivos de imagem (suporta formatos JPG, JPEG, PNG).
*   Pré-visualização da imagem selecionada diretamente na interface.
*   Campo para inserir um prompt customizado para guiar a extração de texto pelo Gemini.
*   Extração de texto de imagens utilizando a API Google Gemini (modelo `gemini-1.5-flash-latest`).
*   O processamento da API é feito em uma thread separada para não congelar a interface do usuário.
*   Botão "Gerar Documento" (a funcionalidade de geração de documento ainda está em aberto para implementação).
*   Botão "Fechar" para encerrar a aplicação.
*   Feedback visual sobre o status da operação (seleção, processamento, sucesso, erro).

## Pré-requisitos

*   Python 3.7 ou superior.
*   `pip` (gerenciador de pacotes Python).
*   Uma chave de API do Google Gemini. Você pode obter uma em [Google AI Studio](https://aistudio.google.com/app/apikey).

## Configuração e Instalação

1.  **Clone ou Baixe o Projeto:**
    Obtenha o arquivo Python (`caderno_gui.py` ou o nome que você deu a ele) e salve-o em um diretório no seu computador.

2.  **Crie o Arquivo de Variáveis de Ambiente (`.env`):**
    No mesmo diretório onde você salvou o script Python, crie um arquivo chamado `.env`. Este arquivo armazenará sua chave da API do Gemini de forma segura.
    Adicione o seguinte conteúdo ao arquivo `.env`, substituindo `SUA_API_KEY_AQUI` pela sua chave real:

    ```env
    GEMINI_API_KEY=SUA_API_KEY_AQUI
    ```

3.  **Instale as Dependências Python:**
    Abra um terminal ou prompt de comando, navegue até o diretório do projeto e execute o seguinte comando para instalar as bibliotecas necessárias:

    ```bash
    pip install -r requirements.txt
    ```    

## Como Executar

Após configurar o arquivo `.env` e instalar as dependências, você pode executar a aplicação com o seguinte comando no seu terminal ou prompt de comando (certifique-se de estar no diretório do projeto):

```bash
python caderno_gui.py