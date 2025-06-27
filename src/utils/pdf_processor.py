import os
import openai
from PyPDF2 import PdfReader

class PDFProcessor:
    def __init__(self):
        self.client = openai.OpenAI()

    def extract_text_from_pdf(self, file_path):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    def process_pdf(self, file_path):
        texto_peticao = self.extract_text_from_pdf(file_path)

        prompt = f"""
Você é um assistente jurídico especializado em Direito Civil. Analise o texto de uma petição inicial e extraia de forma precisa os seguintes dados jurídicos, sem inventar informações:

1. Nome do AUTOR (parte que ajuizou a ação)
2. Nome do RÉU (parte demandada)
3. Tipo de ação judicial
4. Valor da causa (se houver menção)
5. Fatos apresentados (resuma de forma organizada)
6. Pedidos do autor (em tópicos objetivos)
7. Fundamentos jurídicos apresentados (resuma as teses e artigos mencionados)

Texto da petição:
\"\"\"
{texto_peticao}
\"\"\"

Retorne um JSON no seguinte formato:

{{
  "autor": "...",
  "reu": "...",
  "tipo_acao": "...",
  "valor_causa": "...",
  "fatos": "...",
  "pedidos": ["...", "..."],
  "fundamentos_juridicos": ["...", "..."]
}}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um jurista responsável por interpretar petições iniciais com clareza técnica e exatidão."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )

            content = response.choices[0].message.content.strip()

            # Avaliação extra: segurança na conversão JSON
            import json
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                raise ValueError("A resposta da IA não retornou um JSON válido.")

        except Exception as e:
            raise RuntimeError(f"Erro ao analisar o PDF com IA: {e}")
