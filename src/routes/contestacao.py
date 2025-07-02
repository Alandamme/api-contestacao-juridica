import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

from src.utils.document_generator import DocumentGenerator
from src.utils.validator import validar_dados_advogado
from src.utils.pdf_processor import PDFProcessor

contestacao_bp = Blueprint("contestacao", __name__)
pdf_processor = PDFProcessor()

# Diretórios padrão
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
MODELO_PATH = os.path.join(os.path.dirname(__file__), "..", "modelos", "modelo_contestacao_com_placeholders_pronto.docx")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@contestacao_bp.route("/api/gerar-contestacao", methods=["POST"])
def gerar_contestacao():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Requisição inválida: dados ausentes."}), 400

        dados_advogado = dados.get("dados_advogado", {})
        corpo_ia = dados.get("corpo_contestacao", "")
        dados_extraidos = dados.get("dados_extraidos", {})

        # Validação dos campos obrigatórios do advogado
        campos_obrigatorios = ["nome_advogado", "oab_advogado", "uf_advogado"]
        erros = validar_dados_advogado(dados_advogado, campos_obrigatorios)
        if erros:
            return jsonify({"erro": "Campos obrigatórios ausentes", "detalhes": erros}), 400

        if not corpo_ia.strip():
            return jsonify({"erro": "Corpo da contestação está vazio."}), 400

        nome_autor = dados_extraidos.get("autor", "contestacao").replace(" ", "_")
        nome_arquivo = f"{secure_filename(nome_autor)}_contestacao_final.docx"
        caminho_saida = os.path.join(UPLOAD_FOLDER, nome_arquivo)

        generator = DocumentGenerator(MODELO_PATH)
        generator.gerar_contestacao_word(
            dados_extraidos=dados_extraidos,
            corpo_ia=corpo_ia,
            dados_advogado=dados_advogado,
            output_path=caminho_saida
        )

        return send_file(
            caminho_saida,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        return jsonify({"erro": "Erro ao gerar contestação", "detalhes": str(e)}), 500



