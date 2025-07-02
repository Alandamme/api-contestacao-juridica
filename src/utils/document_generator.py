import os
from docx import Document

class DocumentGenerator:
    def __init__(self, modelo_path: str):
        if not os.path.exists(modelo_path):
            raise FileNotFoundError(f"Modelo não encontrado em: {modelo_path}")
        self.modelo_path = modelo_path

    def gerar_contestacao_word(self, dados_extraidos: dict, corpo_ia: str, dados_advogado: dict, output_path: str) -> str:
        """
        Preenche o modelo .docx com dados e gera novo arquivo.
        """
        doc = Document(self.modelo_path)

        # Placeholders simples
        substituicoes = {
            "[NOME_AUTOR]": dados_extraidos.get("autor", ""),
            "[NOME_REU]": dados_extraidos.get("reu", ""),
            "[TIPO_ACAO]": dados_extraidos.get("tipo_acao", ""),
            "[VALOR_CAUSA]": dados_extraidos.get("valor_causa", ""),
            "[NOME_ADVOGADO]": dados_advogado.get("nome_advogado", ""),
            "[OAB_ADVOGADO]": dados_advogado.get("oab_advogado", ""),
            "[UF_ADVOGADO]": dados_advogado.get("uf_advogado", ""),
            "{{corpo_contestacao}}": corpo_ia.strip()
        }

        for p in doc.paragraphs:
            for key, val in substituicoes.items():
                if key in p.text:
                    inline = p.runs
                    for i in range(len(inline)):
                        if key in inline[i].text:
                            inline[i].text = inline[i].text.replace(key, val)

        # Substituir também em tabelas (cabeçalho ou corpo podem conter)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        for key, val in substituicoes.items():
                            if key in p.text:
                                for run in p.runs:
                                    run.text = run.text.replace(key, val)

        # Salva o novo arquivo preenchido
        doc.save(output_path)
        return output_path
