import PyPDF2
import re
from typing import Dict, List, Optional

class PDFProcessor:
    """
    Classe responsável por processar PDFs de petições iniciais
    e extrair informações relevantes para geração de contestação
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

    def analyze_legal_content(self, text: str) -> Dict:
        """
        Analisa o conteúdo jurídico extraído do PDF
        """
        analysis = {
            'partes': self._extract_parties(text),
            'pedidos': self._extract_requests(text),
            'fatos': self._extract_facts(text),
            'fundamentos_juridicos': self._extract_legal_grounds(text),
            'valor_causa': self._extract_case_value(text),
            'tipo_acao': self._identify_action_type(text)
        }

        # Debug prints para verificação
        print("Autor extraído:", analysis['partes'].get('autor'))
        print("Réu extraído:", analysis['partes'].get('reu'))
        print("Pedidos extraídos:", analysis.get('pedidos'))

        return analysis

    def _extract_parties(self, text: str) -> Dict:
        """
        Extrai informações sobre as partes (autor e réu)
        """
        parties = {
            'autor': None,
            'reu': None
        }

        # Padronize o texto para facilitar busca
        clean_text = text.replace('\n', ' ').replace('\r', ' ')

        # Regex para autor
        autor_patterns = [
            r'(?:AUTOR[^\w]{1,6}|REQUERENTE[^\w]{1,6}|DEMANDANTE[^\w]{1,6}|EXEQUENTE[^\w]{1,6}|PROMOVENTE[^\w]{1,6})([A-ZÁÉÍÓÚÇÂÊÔÃÕÜ][^.,;:\n\r()]{5,100})',
            r'(?:Nome|Razão Social)[^\w]{1,6}([A-ZÁÉÍÓÚÇÂÊÔÃÕÜ][^.,;:\n\r()]{5,100})',
        ]

        # Regex para réu
        reu_patterns = [
            r'(?:R[ÉE]U[^\w]{1,6}|REQUERIDO[^\w]{1,6}|DEMANDADO[^\w]{1,6}|EXECUTADO[^\w]{1,6}|PROMOVIDO[^\w]{1,6})([A-ZÁÉÍÓÚÇÂÊÔÃÕÜ][^.,;:\n\r()]{5,100})'
        ]

        for pattern in autor_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                parties['autor'] = match.group(1).strip().title()
                break

        for pattern in reu_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                parties['reu'] = match.group(1).strip().title()
                break

        return parties

    def _extract_requests(self, text: str) -> List[str]:
        """
        Extrai os pedidos da petição inicial
        """
        requests = []
        # Tenta capturar o bloco dos pedidos usando várias frases-chave
        pedidos_section = re.search(
            r'(?:DOS PEDIDOS|PEDIDOS|REQUERIMENTOS?|Diante do exposto,? requer|Diante do exposto,? pede|Assim, requer|Isto Posto,? requer)[\s\S]{0,1000}?(?=\n[A-Z]{2,}|\.|$)',
            text,
            re.IGNORECASE
        )
        if pedidos_section:
            pedidos_text = pedidos_section.group(0)
            # Extrai linhas com bullet, travessão, letra, número, etc.
            items = re.findall(r'(?:[\-\–•*]|\d+\)|[a-z]\)|[0-9]+\.)\s*([^\n]+)', pedidos_text)
            # Se nada


