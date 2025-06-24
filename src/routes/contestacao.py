import os
from flask import Blueprint, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
from docx import Document
from datetime import datetime
from src.utils.pdf_processor import PDFProcessor

contestacao_bp = Blueprint("contestacao", __name__)
pdf_processor = PDFProcessor()

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")

@contestacao_bp.route("/upload", methods=["POST"])
def upload_pdf():
    if "pdf" not in request.files:
        return jsonify({"erro": "Nenhum arquivo PDF enviado"}), 400

    file = request.files["pdf"]
    if file.filename == "":
        return jsonify({"erro": "Nome de arquivo inválido"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join("/tmp", filename)
    file.save(file_path)

    try:
        dados_extraidos = pdf_processor.process_pdf(file_path)
        # Retorna os dados extraídos e os próprios dados como 'session_file' para simplificar
        return jsonify({"dados_extraidos": dados_extraidos, "session_file": dados_extraidos}), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao processar PDF: {str(e)}"}), 500

@contestacao_bp.route("/gerar-contestacao", methods=["POST"])
def gerar_contestacao():
    data = request.json
    if not data:
        return jsonify({"erro": "JSON ausente"}), 400

    dados_peticao = data.get("session_file") # Agora session_file contém os dados da petição
    dados_advogado = data.get("dados_advogado")

    if not dados_peticao or not dados_advogado:
        return jsonify({"erro": "Dados incompletos para gerar contestação"}), 400

    try:
        doc = Document()

        doc.add_heading("CONTESTAÇÃO", level=1)
        doc.add_paragraph(f"Autor: {dados_peticao.get("autor", "")}")
        doc.add_paragraph(f"Réu: {dados_peticao.get("reu", "")}")
        doc.add_paragraph(f"Tipo da Ação: {dados_peticao.get("tipo_acao", "")}")
        doc.add_paragraph(f"Valor da Causa: R$ {dados_peticao.get("valor_causa", "")}")
        doc.add_heading("Resumo dos Fatos", level=2)
        doc.add_paragraph(dados_peticao.get("fatos", ""))

        doc.add_heading("Pedidos da Petição Inicial", level=2)
        for pedido in dados_peticao.get("pedidos", []):
                   doc.add_paragraph(f"- {pedido}", style='List Bullet')

        doc.add_heading("Fundamentos Jurídicos", level=2)
        for fundamento in dados_peticao.get("fundamentos_juridicos", []):
            doc.add_paragraph(f"- {fundamento}", style='List Bullet')

        doc.add_heading("Dados do Advogado", level=2)
        doc.add_paragraph(f"Nome: {dados_advogado.get("nome_advogado", "")}")
        doc.add_paragraph(f"OAB: {dados_advogado.get("oab", "")}")
        doc.add_paragraph(f"Estado: {dados_advogado.get("estado", "")}")

        # Salvar o arquivo .docx na pasta de uploads
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"contestacao_{timestamp}.docx"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        doc.save(output_path)

        # Retornar uma URL para o arquivo gerado
        return jsonify({
            "message": "Contestação gerada com sucesso!",
            "files": {
                            "word": url_for("download_file", filename=output_filename, _external=True)
            }
        }), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao gerar contestação: {str(e)}"}), 500
