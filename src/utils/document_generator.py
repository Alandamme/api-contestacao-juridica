from docx import Document
import os
from typing import Dict

class DocumentGenerator:
    def __init__(self):
        pass

    def create_word_document_from_template(self, template_path: str, output_path: str, dados: Dict[str, str]) -> None:
        """
        Gera um documento Word com base em um modelo .docx e preenche os placeholders com os dados fornecidos.
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Modelo Word não encontrado em {template_path}")

        doc = Document(template_path)

        for paragraph in doc.paragraphs:
            for chave, valor in dados.items():
                if f"{{{{{chave}}}}}" in paragraph.text:
                    inline = paragraph.runs
                    for i in range(len(inline)):
                        if f"{{{{{chave}}}}}" in inline[i].text:
                            inline[i].text = inline[i].text.replace(f"{{{{{chave}}}}}", valor)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for chave, valor in dados.items():
                        if f"{{{{{chave}}}}}" in cell.text:
                            cell.text = cell.text.replace(f"{{{{{chave}}}}}", valor)

        doc.save(output_path)


