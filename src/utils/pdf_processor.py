import PyPDF2
import os
import json
from openai import OpenAI

class PDFProcessor:
    """
    Processa PDFs de petições iniciais e extrai informações para a contestação usando IA.
    """

    def __init__(self):
        self.extracted_data = {}
        self.client = OpenAI()

    def extract_text_from_pdf(self, file_path: str) -> str:
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")

    def process_pdf(self, file_path: str) -> dict:
        try:
            text = self.extract_text_from_pdf(file_path)
            dados_extraidos = self.extract_data_with_ai(text)
            dados_extraidos['texto_completo'] = text
            self.extracted_data = dados_extraidos
            return dados_extraidos
        except Exception as e:
            raise Exception(f"Erro no processamento do PDF: {str(e)}")

    def extract_data_with_ai(self, text: str) -> dict:
        prompt = f"""
Você é um assistente jurídico especializado em petições iniciais brasileiras.

Extraia e retorne em JSON os seguintes campos (preencha o máximo possível):

- autor: Nome completo, qualificação e endereço do autor
- reu: Nome completo, qualificação e endereço do réu
- tipo_acao: Tipo da ação (por extenso)
- valor_causa: Valor da causa, apenas o número
- fatos: Resumo dos fatos principais
- pedidos: Lista dos pedidos do autor (array)
- fundamentos_juridicos: Lista de artigos de lei, jurisprudências, fundamentos invocados

Se não encontrar, deixe o campo como "" ou [], nunca escreva "não identificado".

Texto da petição inicial:
\"\"\"
{text}
\"\"\"

Responda SOMENTE com o JSON.
"""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um assistente jurídico extrator de dados."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.0
        )

        resposta_texto = response.choices[0].message.content

        try:
            dados = json.loads(resposta_texto)
        except Exception:
            try:
                resposta_texto = resposta_texto[resposta_texto.find("{"):resposta_texto.rfind("}")+1]
                dados = json.loads(resposta_texto)
            except Exception as e:
                raise Exception(f"Erro ao interpretar resposta JSON: {str(e)}\nResposta:\n{resposta_texto}")

        return dados
