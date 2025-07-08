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

    def extract_json_from_text(self, texto):
        try:
            match = re.search(r"\{[\s\S]+\}", texto)
            if not match:
                raise ValueError("Nenhum JSON encontrado na resposta da IA.")
            return json.loads(match.group(0))
        except Exception as e:
            raise Exception(f"Erro ao converter resposta da IA para JSON: {e}")

    def analyze_pdf_with_ai(self, pdf_text):
        prompt = f"""
Você é um advogado especialista em direito cível. Com base na petição inicial abaixo, extraia os seguintes dados no formato JSON EXATAMENTE como mostrado, sem explicações ou comentários fora do JSON:

Modelo:
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
\"\"\"
{self.reduzir_texto(pdf_text, 5000)}
\"\"\"
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
            resposta = response.choices[0].message.content.strip()
            return self.extract_json_from_text(resposta)
        except Exception as e:
            raise Exception(f"Erro ao analisar o PDF com IA: {e}")

    def process_pdf(self, file_path):
        texto_pdf = self.extract_text_from_pdf(file_path)
        return self.analyze_pdf_with_ai(texto_pdf)
