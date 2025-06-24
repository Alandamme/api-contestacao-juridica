import os
import tempfile
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from src.services.pdf_processor import PDFProcessor  # Certifique-se de que esse caminho está correto

contestacao_bp = Blueprint('contestacao', __name__)

@contestacao_bp.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['pdf']

    if file.filename == '':
        return jsonify({'error': 'Nome do arquivo inválido'}), 400

    try:
        # Salva temporariamente
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)

        # Processa com IA
        processor = PDFProcessor()
        dados = processor.process_pdf(file_path)

        return jsonify({'status': 'ok', 'dados_extraidos': dados})

    except Exception as e:
        return jsonify({'error': f'Erro ao processar PDF: {str(e)}'}), 500

