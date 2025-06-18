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
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        prompt = f"""
Você é um assistente jurídico especializado em leitura de petições iniciais brasileiras.

Seu objetivo é retornar **apenas um JSON** preenchendo o máximo de dados possíveis, mesmo que alguns estejam incompletos.

**Campos obrigatórios:**
- "autor": Tente extrair o nome completo do autor, buscando padrões como "vem propor a presente", "em face de", "AUTOR", "REQUERENTE" ou similares e pegue o nome ou a parte seguinte, mesmo que não tenha tudo (RG, CPF, profissão, endereço);
- "reu": Tente extrair o nome completo do réu, buscando padrões como "em face de", "RÉU", "REQUERIDO" ou similares e pegue o nome ou a razão social, mesmo se faltar endereço ou CNPJ;
- "tipo_acao": tipo da ação, por extenso (ex: "ação de indenização por danos materiais e morais")
- "valor_causa": valor total da causa, apenas o número
- "fatos": resumo dos fatos principais, bem objetivo
- "pedidos": lista (array) dos principais pedidos feitos pelo autor
- "fundamentos_juridicos": lista de artigos de lei, CDC, jurisprudências e fundamentos invocados

IMPORTANTE:
- Sempre preencha o campo com o texto mais próximo do PDF, mesmo se não estiver completo.
- Não retorne "não identificado", nem "[não encontrado]", preencha com o que for possível.
- Se um campo não existir, deixe-o como string vazia ou lista vazia, mas nunca com o texto "não identificado".
- NÃO inclua explicação, só o JSON.

Texto da petição inicial:
\"\"\"
{text}
\"\"\"

Responda SOMENTE com o JSON solicitado acima, sem explicações, sem texto fora do JSON.
"""
        response = client.chat.completions.create(
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
            # Se não vier JSON válido, tente limpar manualmente
            resposta_texto = resposta_texto[resposta_texto.find("{"):resposta_texto.rfind("}")+1]
            dados = json.loads(resposta_texto)
        return dados
