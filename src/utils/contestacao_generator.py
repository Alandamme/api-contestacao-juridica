import os
import uuid
from .document_generator import WordContestacaoGenerator


def gerar_contestacao_ia_formatada(dados_extraidos, dados_reu):
    id_contestacao = str(uuid.uuid4())
    nome_arquivo = f"{id_contestacao}.docx"
    caminho_saida = os.path.join("uploads", nome_arquivo)

    modelo_path = os.path.join("src", "static", "modelos", "modelo_contestacao_com_placeholders.docx")
    gerador = WordContestacaoGenerator(modelo_path)
    gerador.gerar_contestacao(dados_extraidos, dados_reu, caminho_saida)

    return {
        "contestacao_id": id_contestacao,
        "arquivo_path": caminho_saida,
        "preview": f"Contestação gerada com sucesso para o réu {dados_reu.get('advogado_reu', '')}."
    }

