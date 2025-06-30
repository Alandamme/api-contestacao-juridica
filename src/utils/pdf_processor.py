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

    def reduzir_texto(self, texto, limite=7000):
        if len(texto) > limite:
            return texto[:limite] + "\n[Texto truncado por limite de tokens]"
        return texto

    def analyze_pdf_with_ai(self, pdf_text):
        prompt = f"""
Você é um advogado especialista em Direito Civil e Processo Civil.

Leia cuidadosamente a petição inicial abaixo e faça:

1️⃣ **Extraia** (se possível) em formato JSON os seguintes dados:
- Nome do autor
- Nome do réu
- Tipo da ação
- Valor da causa
- Fatos principais (resumo)
- Pedidos do autor
- Fundamentos jurídicos apresentados

2️⃣ **Analise tecnicamente** a petição inicial: destaque possíveis pontos frágeis do pedido, teses jurídicas que podem ser exploradas na contestação e observações relevantes para a defesa.

Retorne EXATAMENTE neste formato JSON:
```
{{
  "autor": "...",
  "reu": "...",
  "tipo_acao": "...",
  "valor_causa": "...",
  "fatos": "...",
  "pedidos": ["...", "..."],
  "fundamentos_juridicos": ["...", "..."],
  "analise_juridica": "Aqui um texto técnico e atual sobre possíveis linhas de defesa, preliminares, teses e observações."
}}

Petição inicial:
"""
{self.reduzir_texto(pdf_text, 7000)}
"""
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um advogado especializado em petições cíveis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            result_text = response.choices[0].message.content.strip()
            result_json = json.loads(result_text)
            return result_json
        except Exception as e:
            raise Exception(f"Erro ao analisar o PDF com IA: {e}")

    def process_pdf(self, file_path):
        pdf_text = self.extract_text_from_pdf(file_path)
        return self.analyze_pdf_with_ai(pdf_text)
