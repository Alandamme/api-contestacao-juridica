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
        
        Args:
            file_path (str): Caminho para o arquivo PDF
            
        Returns:
            str: Texto extraído do PDF
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
                
                return text
        except Exception as e:
            raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")
    
    def analyze_legal_content(self, text: str) -> Dict:
        """
        Analisa o conteúdo jurídico extraído do PDF
        
        Args:
            text (str): Texto extraído do PDF
            
        Returns:
            Dict: Dicionário com informações estruturadas
        """
        analysis = {
            'partes': self._extract_parties(text),
            'pedidos': self._extract_requests(text),
            'fatos': self._extract_facts(text),
            'fundamentos_juridicos': self._extract_legal_grounds(text),
            'valor_causa': self._extract_case_value(text),
            'tipo_acao': self._identify_action_type(text)
        }
        
        return analysis
    
    def _extract_parties(self, text: str) -> Dict:
        """
        Extrai informações sobre as partes (autor e réu)
        """
        parties = {
            'autor': None,
            'reu': None
        }
        
        # Padrões para identificar autor
        autor_patterns = [
            r'(?:AUTOR|REQUERENTE|DEMANDANTE)[\s:]+([^\n]+)',
            r'(?:Nome|Razão Social)[\s:]+([^\n]+)',
        ]
        
        # Padrões para identificar réu
        reu_patterns = [
            r'(?:RÉU|REQUERIDO|DEMANDADO)[\s:]+([^\n]+)',
        ]
        
        for pattern in autor_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parties['autor'] = match.group(1).strip()
                break
        
        for pattern in reu_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parties['reu'] = match.group(1).strip()
                break
        
        return parties
    
    def _extract_requests(self, text: str) -> List[str]:
        """
        Extrai os pedidos da petição inicial
        """
        requests = []
        
        # Procurar seção de pedidos
        pedidos_section = re.search(
            r'(?:DOS PEDIDOS|PEDIDOS|REQUERIMENTOS?)[\s\S]*?(?=\n[A-Z]{2,}|\Z)',
            text,
            re.IGNORECASE
        )
        
        if pedidos_section:
            pedidos_text = pedidos_section.group(0)
            # Extrair itens numerados ou com letras
            items = re.findall(r'(?:[a-z]\)|[0-9]+\.)\s*([^\n]+)', pedidos_text, re.IGNORECASE)
            requests.extend(items)
        
        return requests
    
    def _extract_facts(self, text: str) -> str:
        """
        Extrai a narrativa dos fatos
        """
        # Procurar seção dos fatos
        fatos_patterns = [
            r'(?:DOS FATOS|FATOS|NARRATIVA)[\s\S]*?(?=\n[A-Z]{2,})',
            r'(?:HISTÓRICO|RELATO)[\s\S]*?(?=\n[A-Z]{2,})'
        ]
        
        for pattern in fatos_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return ""
    
    def _extract_legal_grounds(self, text: str) -> List[str]:
        """
        Extrai os fundamentos jurídicos citados
        """
        legal_grounds = []
        
        # Procurar citações de leis, artigos, etc.
        law_patterns = [
            r'(?:Lei|Código|Decreto|Portaria)\s+n?º?\s*[\d\./]+',
            r'(?:Art|Artigo)\.?\s*\d+',
            r'(?:CF|Constituição Federal)',
            r'(?:CDC|Código de Defesa do Consumidor)',
            r'(?:CPC|Código de Processo Civil)'
        ]
        
        for pattern in law_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            legal_grounds.extend(matches)
        
        return list(set(legal_grounds))  # Remove duplicatas
    
    def _extract_case_value(self, text: str) -> Optional[str]:
        """
        Extrai o valor da causa
        """
        value_patterns = [
            r'(?:valor da causa|valor atribuído)[\s:]+R\$\s*([\d.,]+)',
            r'R\$\s*([\d.,]+)'
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _identify_action_type(self, text: str) -> str:
        """
        Identifica o tipo de ação com base no conteúdo
        """
        action_types = {
            'indenização': ['indenização', 'danos morais', 'danos materiais'],
            'cobrança': ['cobrança', 'débito', 'pagamento'],
            'rescisão': ['rescisão', 'resolução contratual'],
            'revisional': ['revisão', 'revisional', 'redução'],
            'consignação': ['consignação', 'depósito']
        }
        
        text_lower = text.lower()
        
        for action_type, keywords in action_types.items():
            if any(keyword in text_lower for keyword in keywords):
                return action_type
        
        return 'não identificado'
    
    def process_pdf(self, file_path: str) -> Dict:
        """
        Processa completamente um PDF de petição inicial
        
        Args:
            file_path (str): Caminho para o arquivo PDF
            
        Returns:
            Dict: Dados estruturados extraídos do PDF
        """
        try:
            # Extrair texto
            text = self.extract_text_from_pdf(file_path)
            
            # Analisar conteúdo
            analysis = self.analyze_legal_content(text)
            
            # Adicionar texto completo para referência
            analysis['texto_completo'] = text
            
            self.extracted_data = analysis
            return analysis
            
        except Exception as e:
            raise Exception(f"Erro no processamento do PDF: {str(e)}")

