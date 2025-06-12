"""
Gerador de documentos para contestações jurídicas
"""

from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

class DocumentGenerator:
    """
    Classe responsável por gerar documentos Word formatados
    """
    
    def __init__(self):
        pass
    
    def create_word_document(self, contestacao_text: str, filename: str) -> str:
        """
        Cria um documento Word formatado com a contestação
        
        Args:
            contestacao_text (str): Texto da contestação
            filename (str): Nome do arquivo
            
        Returns:
            str: Caminho do arquivo gerado
        """
        # Criar novo documento
        doc = Document()
        
        # Configurar margens
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1.2)
            section.right_margin = Inches(1)
        
        # Dividir o texto em parágrafos
        paragraphs = contestacao_text.split('\n\n')
        
        for para_text in paragraphs:
            if para_text.strip():
                # Adicionar parágrafo
                paragraph = doc.add_paragraph()
                
                # Verificar se é título (texto em maiúsculas)
                if para_text.isupper() and len(para_text) < 100:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = paragraph.add_run(para_text)
                    run.bold = True
                else:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    paragraph.add_run(para_text)
                
                # Espaçamento entre parágrafos
                paragraph.space_after = Inches(0.1)
        
        # Salvar documento
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        file_path = os.path.join(output_dir, filename)
        doc.save(file_path)
        
        return file_path
    
    def create_pdf_from_text(self, contestacao_text: str, filename: str) -> str:
        """
        Cria um PDF a partir do texto da contestação
        
        Args:
            contestacao_text (str): Texto da contestação
            filename (str): Nome do arquivo (sem extensão)
            
        Returns:
            str: Caminho do arquivo PDF gerado
        """
        # Criar diretório de saída
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Criar arquivo markdown temporário
        md_filename = filename.replace('.pdf', '.md')
        md_path = os.path.join(output_dir, md_filename)
        
        # Formatar texto para markdown
        md_content = self._format_text_to_markdown(contestacao_text)
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        # Converter para PDF usando manus-md-to-pdf
        pdf_path = os.path.join(output_dir, filename)
        
        try:
            import subprocess
            result = subprocess.run(
                ['manus-md-to-pdf', md_path, pdf_path],
                capture_output=True,
                text=True,
                cwd=output_dir
            )
            
            if result.returncode == 0:
                # Remover arquivo markdown temporário
                os.remove(md_path)
                return pdf_path
            else:
                raise Exception(f"Erro na conversão para PDF: {result.stderr}")
                
        except Exception as e:
            # Se falhar, manter o arquivo markdown
            return md_path
    
    def _format_text_to_markdown(self, text: str) -> str:
        """
        Formata o texto da contestação para markdown
        """
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append('')
                continue
            
            # Títulos principais (texto em maiúsculas)
            if line.isupper() and len(line) < 100:
                formatted_lines.append(f'# {line}')
            # Seções numeradas
            elif line.startswith(('I -', 'II -', 'III -', 'IV -', 'V -')):
                formatted_lines.append(f'## {line}')
            # Subseções
            elif any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', 'a)', 'b)', 'c)']):
                formatted_lines.append(f'### {line}')
            else:
                formatted_lines.append(line)
        
        return '\n\n'.join(formatted_lines)

