import os
from docx import Document
from docx.shared import Pt
from datetime import datetime


class WordContestacaoGenerator:
    """
    Gera uma contestação em formato .docx a partir de dados extraídos de uma petição inicial e do modelo base do escritório.
    """

    def __init__(self, modelo_path: str):
        if not os.path.exists(modelo_path):
            raise FileNotFoundError(f"Modelo DOCX não encontrado: {modelo_path}")
        self.modelo_path = modelo_path

    def gerar_contestacao(self, dados_extraidos: dict, dados_reu: dict, salvar_em: str) -> str:
        doc = Document(self.modelo_path)

        # Substituições simples por placeholders do modelo
        placeholders = {
            "[NOME_AUTOR]": dados_extraidos.get("autor", {}).get("nome", "NOME DO AUTOR"),
            "[QUALIFICACAO_AUTOR]": dados_extraidos.get("autor", {}).get("qualificacao", ""),
            "[ENDERECO_AUTOR]": dados_extraidos.get("autor", {}).get("endereco", ""),

            "[NOME_REU]": dados_extraidos.get("reu", {}).get("nome", "NOME DO RÉU"),
            "[QUALIFICACAO_REU]": dados_extrairos.get("reu", {}).get("qualificacao", ""),
            "[ENDERECO_REU]": dados_extraidos.get("reu", {}).get("endereco", ""),

            "[TIPO_ACAO]": dados_extraidos.get("tipo_acao", ""),
            "[VALOR_CAUSA]": dados_extraidos.get("valor_causa", ""),

            "[RESUMO_FATOS]": dados_extraidos.get("fatos", ""),

            "[PEDIDOS]": '\n'.join(f"- {p}" for p in dados_extraidos.get("pedidos", [])),
            "[FUNDAMENTOS]": '\n'.join(f"- {f}" for f in dados_extraidos.get("fundamentos_juridicos", [])),

            "[NOME_ADVOGADO]": dados_reu.get("advogado_reu", ""),
            "[OAB_NUMERO]": dados_reu.get("oab_numero", ""),
            "[UF]": dados_reu.get("estado", ""),
            "[DATA]": datetime.today().strftime("%d/%m/%Y")
        }

        for paragraph in doc.paragraphs:
            for key, value in placeholders.items():
                if key in paragraph.text:
                    paragraph.text = paragraph.text.replace(key, value)
                    for run in paragraph.runs:
                        run.font.size = Pt(12)

        doc.save(salvar_em)
        return salvar_em

