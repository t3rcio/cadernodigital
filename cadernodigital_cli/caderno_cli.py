import google.generativeai as genai
import os
import sys
import argparse
from PIL import Image # Usado para carregar a imagem e inferir o MIME type

import logging
from settings import FORMAT_DATE, LOG_FILENAME, FORMAT_DATE_TIME, GOOGLE_API_KEY
from datetime import datetime
from docx import Document

logging.basicConfig(
    filename='{}'.format(LOG_FILENAME)
)

GEMINI_MODEL = 'gemini-1.5-flash'

def extract_text_from_image(api_key, image_path, prompt_text):
    """
    Envia uma imagem para a API do Gemini e extrai o texto.
    """
    try:
        genai.configure(api_key=api_key)

        # Tenta carregar a imagem e inferir o MIME type
        try:
            img = Image.open(image_path)
            # Converte para um formato comum como JPEG para garantir compatibilidade
            # e para obter os bytes facilmente.
            # O Gemini suporta PNG, JPEG, WEBP, HEIC, HEIF
            if img.format == "PNG":
                mime_type = "image/png"
            elif img.format == "WEBP":
                mime_type = "image/webp"
            elif img.format == "HEIC":
                mime_type = "image/heic"
            elif img.format == "HEIF":
                mime_type = "image/heif"
            else: # Default to JPEG for other types or if conversion is needed
                mime_type = "image/jpeg"

            # Lê os bytes da imagem diretamente do arquivo
            with open(image_path, 'rb') as f:
                image_bytes = f.read()

        except FileNotFoundError:
            return f"Erro: Arquivo de imagem não encontrado em '{image_path}'"
        except Exception as e:
            return f"Erro ao processar a imagem: {e}"

        # Modelo que suporta visão (imagens)
        model = genai.GenerativeModel(GEMINI_MODEL)

        # Monta o conteúdo da requisição
        # A ordem é importante: texto primeiro, depois a imagem para `gemini-pro-vision`
        # Ou uma lista de partes, onde uma é texto e outra é a imagem.
        contents = [
            prompt_text, # Seu prompt
            {'mime_type': mime_type, 'data': image_bytes} # Dados da imagem
        ]

        # Faz a requisição
        print(f"Enviando imagem '{image_path}' para análise...")
        response = model.generate_content(contents)

        # Verifica se houve bloqueio por segurança
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            return f"Conteúdo bloqueado pela API: {response.prompt_feedback.block_reason}"

        # Extrai o texto da resposta
        if response.candidates and response.candidates[0].content.parts:
            extracted_text = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
            return extracted_text.strip() if extracted_text else "Nenhum texto encontrado ou a resposta não continha texto."
        else:
            return "Não foi possível extrair texto da resposta da API."

    except Exception as e:
        logging.error(str(e))
        return f"Ocorreu um erro na API do Gemini: {e}"
    

def cria_documento(resultado, titulo, saida):
    documento = Document()
    try:
        if not resultado:
            print("Não há manuscrito na imagem a ser salvo")
            sys.exit(0)
        
        for p in resultado.split('\n'):
            documento.add_paragraph(p)
        documento.save(saida)
        print("Documento salvo!")
    
    except Exception as error:
        logging.error(str(error))
        print("Ocorreu um erro ao salvar o documento")
    

if __name__ == "__main__":
    agora = datetime.now()
    parser = argparse.ArgumentParser(description="Extrai texto manuscrito de uma imagem usando a API do Gemini.")
    parser.add_argument("image_path", help="Caminho para o arquivo de imagem (ex: foto_caderno.jpg)")
    parser.add_argument(
        "--prompt",
        type=str,
        default="Extraia todo o texto manuscrito visível nesta imagem. Transcreva-o da forma mais fiel possível.",
        help="Prompt para guiar a extração de texto."
    )
    parser.add_argument(
        '--titulo',
        type=str,
        default='Documento criado em {}'.format(agora.strftime(FORMAT_DATE_TIME)),
        help='Informe o titulo do documento'
    )
    parser.add_argument(
        '--nome',
        help='Nome do arquivo a ser salvo',
        default=agora.strftime(FORMAT_DATE_TIME)
    )
    parser.add_argument(
        '--doc',
        type=str,
        help='Onde salvar o arquivo documento',
        default = '/home/tercio/Documentos/{}.docx'.format(agora.strftime(FORMAT_DATE_TIME))
    )
    args = parser.parse_args()
    api_key = GOOGLE_API_KEY
    
    if not api_key:
        print("Erro: A variável de ambiente GOOGLE_API_KEY não está configurada.")
        print("Por favor, defina-a com sua chave da API do Google AI Studio.")
        sys.exit(1)

    resultado = extract_text_from_image(api_key, args.image_path, args.prompt)
    cria_documento(resultado, titulo=args.titulo, saida=args.doc)
    sys.exit(0)
    