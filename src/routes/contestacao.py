# src/routes/contestacao.py

import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from docx import Document
from src.utils.document_generator import substituir_placeholders
from src.utils.pdf_processor import PDFProcessor
from src.utils.validator import validar_dados_advogado

contestacao_bp = Blueprint("contestacao", __name__)
pdf_processor = PDFProcessor()

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MODELO_PATH = os.path.join(os.path.dirname(__file__), "..", "modelos", "modelo_contestacao_com_placeholders_pronto.docx")


@contestacao_bp.route("/api/gerar-contestacao", methods=["POST"])
def gerar_contestacao():
    try:
        # Obtém JSON da requisição
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Requisição inválida, dados ausentes."}), 400

        dados_advogado = dados.get("dados_advogado", {})
        corpo_contestacao = dados.get("corpo_contestacao", "")

        # Valida os dados obrigatórios do advogado
        campos_obrigatorios = ["nome_advogado", "oab", "estado"]
        erros = validar_dados_advogado(dados_advogado, campos_obrigatorios)
        if erros:
            return jsonify({"erro": "Campos obrigatórios ausentes", "detalhes": erros}), 400

        if not corpo_contestacao.strip():
            return jsonify({"erro": "Corpo da contestação está vazio"}), 400

        # Prepara nome do arquivo
        nome_autor = dados.get("autor", "contestacao").replace(" ", "_")
        nome_arquivo = f"{secure_filename(nome_autor)}_contestacao_final.docx"
        caminho_saida = os.path.join(UPLOAD_FOLDER, nome_arquivo)

        # Gera documento final substituindo os placeholders no modelo
        substituir_placeholders(
            modelo_path=MODELO_PATH,
            saida_path=caminho_saida,
            dados={
                "corpo_contestacao": corpo_contestacao,
                "nome_advogado": dados_advogado["nome_advogado"],
                "oab": dados_advogado["oab"],
                "estado": dados_advogado["estado"]
            }
        )

        return send_file(
            caminho_saida,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        return jsonify({"erro": "Erro ao gerar contestação", "detalhes": str(e)}), 500


