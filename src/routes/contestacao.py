import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from docx import Document
from tempfile import NamedTemporaryFile
from src.utils.pdf_processor import PDFProcessor

contestacao_bp = Blueprint('contestacao', __name__)
pdf_processor = PDFProcessor()

@contestacao_bp.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'erro': 'Nenhum arquivo PDF enviado'}), 400

    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'erro': 'Nome de arquivo inválido'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join('/tmp', filename)
    file.save(file_path)

    try:
        dados = pdf_processor.process_pdf(file_path)
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': f'Erro ao processar PDF: {str(e)}'}), 500

@contestacao_bp.route('/gerar-contestacao', methods=['POST'])
def gerar_contestacao():
    dados = request.json
    if not dados:
        return jsonify({'erro': 'JSON ausente'}), 400

    try:
        doc = Document()

        doc.add_heading('CONTESTAÇÃO', level=1)
        doc.add_paragraph(f"Autor: {dados.get('autor', '')}")
        doc.add_paragraph(f"Réu: {dados.get('reu', '')}")
        doc.add_paragraph(f"Tipo da Ação: {dados.get('tipo_acao', '')}")
        doc.add_paragraph(f"Valor da Causa: R$ {dados.get('valor_causa', '')}")
        doc.add_heading('Resumo dos Fatos', level=2)
        doc.add_paragraph(dados.get('fatos', ''))

        doc.add_heading('Pedidos da Petição Inicial', level=2)
        for pedido in dados.get('pedidos', []):
            doc.add_paragraph(f"- {pedido}", style='List Bullet')

        doc.add_heading('Fundamentos Jurídicos', level=2)
        for fundamento in dados.get('fundamentos_juridicos', []):
            doc.add_paragraph(f"- {fundamento}", style='List Bullet')

        # Gerar o arquivo .docx em arquivo temporário
        with NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
            doc.save(tmp.name)
            tmp_path = tmp.name

        return send_file(tmp_path, as_attachment=True, download_name='contestacao.docx')
    except Exception as e:
        return jsonify({'erro': f'Erro ao gerar contestação: {str(e)}'}), 500
