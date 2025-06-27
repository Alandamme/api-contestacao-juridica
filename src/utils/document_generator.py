import os
from docx import Document
from datetime import datetime


class WordContestacaoGenerator:
    """
    Gera uma contestação em formato .docx preservando a formatação do modelo original do escritório.
    Substitui os placeholders como [NOME_AUTOR], [NOME_REU], {{corpo_contestacao}}, etc.
    """

    def __init__(self, modelo_path: str):
        if not os.path.exists(modelo_path):
            raise FileNotFoundError(f"Modelo DOCX não encontrado: {modelo_path}")
        self.modelo_path = modelo_path

    def gerar_contestacao(self, dados_extraidos: dict, dados_reu: dict, corpo_ia: str, salvar_em: str) -> str:
        doc = Document(self.modelo_path)

        # Prepara os dados substituíveis
        placeholders = {
            "[NOME_AUTOR]": dados_extraidos.get("autor", {}).get("nome", "NOME DO AUTOR"),
            "[QUALIFICACAO_AUTOR]": dados_extraidos.get("autor", {}).get("qualificacao", ""),
            "[ENDERECO_AUTOR]": dados_extraidos.get("autor", {}).get("endereco", ""),

            "[NOME_REU]": dados_extraidos.get("reu", {}).get("nome", "NOME DO RÉU"),
            "[QUALIFICACAO_REU]": dados_extraidos.get("reu", {}).get("qualificacao", ""),
            "[ENDERECO_REU]": dados_extraidos.get("reu", {}).get("endereco", ""),

            "[TIPO_ACAO]": dados_extraidos.get("tipo_acao", ""),
            "[VALOR_CAUSA]": dados_extraidos.get("valor_causa", ""),

            "[RESUMO_FATOS]": dados_extraidos.get("fatos", ""),

            "[PEDIDOS]": '\n'.join(f"- {p}" for p in dados_extraidos.get("pedidos", [])),
            "[FUNDAMENTOS]": '\n'.join(f"- {f}" for f in dados_extraidos.get("fundamentos_juridicos", [])),

            "[NOME_ADVOGADO]": dados_reu.get("advogado_reu", ""),
            "[OAB_NUMERO]": dados_reu.get("oab_numero", ""),
            "[UF]": dados_reu.get("estado", ""),
            "[DATA]": datetime.today().strftime("%d/%m/%Y"),

            "{{corpo_contestacao}}": corpo_ia.strip()
        }

        # Substitui os placeholders mantendo a formatação
        for paragraph in doc.paragraphs:
            for key, value in placeholders.items():
                if key in paragraph.text:
                    inline = paragraph.runs
                    for i in range(len(inline)):
                        if key in inline[i].text:
                            inline[i].text = inline[i].text.replace(key, value)

        # Substituição em tabelas, se houver
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        for key, value in placeholders.items():
                            if key in paragraph.text:
                                inline = paragraph.runs
                                for i in range(len(inline)):
                                    if key in inline[i].text:
                                        inline[i].text = inline[i].text.replace(key, value)

        doc.save(salvar_em)
        return salvar_em

