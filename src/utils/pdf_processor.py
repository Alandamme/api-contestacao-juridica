import os
import json
import fitz  # PyMuPDF
from openai import OpenAI

class PDFProcessor:
    def __init__(self):
        self.client = OpenAI()

    def extract_text_from_pdf(self, file_path):
        """Extrai texto usando PyMuPDF (fitz), que é mais eficiente e confiável que PyPDF2"""
        try:
            doc = fitz.open(file_path)
            texto = "\n".join(page.get_text() for page in doc)
            doc.close()
            return texto.strip()
        except Exception as e:
            raise Exception(f"Erro ao extrair texto do PDF: {e}")

    def reduzir_texto(self, texto, limite=5000):
        texto = texto.strip()
        return texto[:limite] + "\n\n[Texto truncado por limite de tokens]" if len(texto) > limite else texto

    def analyze_pdf_with_ai(self, pdf_text):
        prompt = f"""
Você é um advogado especializado em Direito Civil. Analise a petição inicial abaixo e extraia os dados conforme o formato JSON indicado:

Texto da petição:
\"\"\"
{self.reduzir_texto(pdf_text, 5000)}
\"\"\"

Retorne SOMENTE neste formato JSON:
{{
  "autor": "...",
  "reu": "...",
  "tipo_acao": "...",
  "valor_causa": "...",
  "fatos": "...",
  "pedidos": ["..."],
  "fundamentos_juridicos": ["..."]
}}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um advogado cível especialista em análise de petições."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            result_text = response.choices[0].message.content.strip()
            result_text = result_text.replace("```json", "").replace("```", "").strip()

            return json.loads(result_text)

        except json.JSONDecodeError:
            raise Exception(f"Erro: A IA retornou JSON inválido:\n{result_text}")
        except Exception as e:
            raise Exception(f"Erro ao analisar o PDF com IA: {e}")

    def process_pdf(self, file_path):
        texto = self.extract_text_from_pdf(file_path)
        return self.analyze_pdf_with_ai(texto)

