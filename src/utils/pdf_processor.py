import os
import re
import json
from openai import OpenAI
from PyPDF2 import PdfReader

class PDFProcessor:
    def __init__(self):
        self.client = OpenAI()

    def extract_text_from_pdf(self, file_path):
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text.strip()
        except Exception as e:
            raise Exception(f"Erro ao extrair texto do PDF: {e}")

    def reduzir_texto(self, texto, limite=5000):
        if len(texto) > limite:
            return texto[:limite] + "\n[Texto truncado por limite de tokens]"
        return texto

    def analyze_pdf_with_ai(self, pdf_text):
        prompt = f"""
Você é um advogado especialista em direito cível. Analise o texto da petição inicial abaixo e extraia as seguintes informações de forma clara e objetiva, organizadas em formato JSON:

1. Nome do autor da ação.
2. Nome do réu.
3. Tipo de ação ou natureza do pedido (Ex: Ação de Cobrança, Indenização, etc).
4. Valor da causa.
5. Fatos principais (resumo em até 5 linhas).
6. Pedidos do autor.
7. Fundamentos jurídicos invocados na petição.

Retorne exatamente no seguinte formato JSON:
{{
  "autor": "...",
  "reu": "...",
  "tipo_acao": "...",
  "valor_causa": "...",
  "fatos": "...",
  "pedidos": ["...", "..."],
  "fundamentos_juridicos": ["...", "..."]
}}

Petição inicial:
"""
{self.reduzir_texto(pdf_text, 5000)}
"""
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um advogado especializado em direito cível."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1200
            )
            result_text = response.choices[0].message.content.strip()
            result_json = json.loads(result_text)
            return result_json
        except Exception as e:
            raise Exception(f"Erro ao analisar o PDF com IA: {e}")

    def process_pdf(self, file_path):
        pdf_text = self.extract_text_from_pdf(file_path)
        return self.analyze_pdf_with_ai(pdf_text)
