from docx import Document
from typing import Dict
import os

class DocumentGenerator:
    def __init__(self):
        pass

    def create_word_document_from_template(self, template_path: str, output_path: str, dados: Dict[str, str]) -> None:
        """
        Preenche um documento Word (.docx) com base em um template e substitui os placeholders {{chave}} pelos dados.
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Modelo Word não encontrado em: {template_path}")

        doc = Document(template_path)

        # Substitui em parágrafos
        for paragraph in doc.paragraphs:
            self._substituir_placeholders_paragraph(paragraph, dados)

        # Substitui em tabelas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._substituir_placeholders_paragraph(paragraph, dados)

        # Substitui em cabeçalho e rodapé, se existir
        for section in doc.sections:
            if section.header:
                for paragraph in section.header.paragraphs:
                    self._substituir_placeholders_paragraph(paragraph, dados)
            if section.footer:
                for paragraph in section.footer.paragraphs:
                    self._substituir_placeholders_paragraph(paragraph, dados)

        doc.save(output_path)

    def _substituir_placeholders_paragraph(self, paragraph, dados: Dict[str, str]):
        """
        Substitui os placeholders dentro de um parágrafo.
        """
        for chave, valor in dados.items():
            placeholder = f"{{{{{chave}}}}}"
            if placeholder in paragraph.text:
                for run in paragraph.runs:
                    if placeholder in run.text:
                        run.text = run.text.replace(placeholder, valor.strip())
