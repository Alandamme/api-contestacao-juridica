import PyPDF2
import re
import os
import json
from typing import Dict, List, Optional

from openai import OpenAI

class PDFProcessor:
    """
    Classe responsável por processar PDFs de petições iniciais
    e extrair informações relevantes para geração de contestação
    usando IA (OpenAI).
    """

    def __init__(self):
        self.extracted_data = {}

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extrai todo o texto de um arquivo PDF
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")

    def process_pdf(self, file_path: str) -> dict:
        """
        Processa um PDF e usa IA para extrair dados jurídicos relevantes.
        """
        try:
            text = self.extract_text_from_pdf(file_path)
            dados_extraidos = self.extract_data_with_ai(text)
            # Salve o texto completo também, se quiser
            dados_extraidos['texto_completo'] = text
            self.extracted_data = dados_extraidos
            return dados_extraidos
        except Exception as e:
            raise Exception(f"Erro no processamento do PDF: {str(e)}")

    def extract_data_with_ai(self, text: str) -> dict:
        """
        Usa OpenAI GPT para extrair partes, valor da causa, pedidos, fatos, fundamentos jurídicos do texto da petição.
        """
        # PRINT PARA DEBUG DA VARIÁVEL DE AMBIENTE
        print("PDFProcessor: OPENAI_API_KEY:", os.environ.get("OPENAI_API_KEY"))

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        prompt = f"""
Você é um assistente jurídico. Extraia e retorne em JSON, a partir do texto da petição inicial abaixo, os seguintes campos:

- autor: nome completo, qualificação e endereço do autor
- reu: nome completo, qualificação e endereço do réu
- tipo_acao: tipo da ação (ex: indenização, cobrança)
- valor_causa: valor total da causa
- fatos: resumo dos fatos relevantes do caso
- pedidos: lista dos principais pedidos feitos pelo autor
- fundamentos_juridicos: lista de artigos de lei, CDC, jurisprudências e fundamentos invocados

Texto da petição inicial:
\"\"\"
{text}
\"\"\"

Retorne **somente** o JSON com esses campos, não explique nada.
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um assistente jurídico extrator de dados."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.0
        )

        resposta_texto = response.choices[0].message.content
        try:
            dados = json.loads(resposta_texto)
        except Exception:
            # Se não vier JSON válido, tente limpar manualmente
            resposta_texto = resposta_texto[resposta_texto.find("{"):resposta_texto.rfind("}")+1]
            dados = json.loads(resposta_texto)
        return dados
