import os
import uuid
import json
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from src.utils.pdf_processor import PDFProcessor  # Refatorado para ser mais limpo

upload_bp = Blueprint('upload_bp', __name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@upload_bp.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'Arquivo não encontrado.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo inválido.'}), 400

    filename = secure_filename(file.filename)
    session_id = str(uuid.uuid4())
    filepath = os.path.join(UPLOAD_FOLDER, f"{session_id}_{filename}")
    file.save(filepath)

    try:
        processor = PDFProcessor()
        dados = processor.process_pdf(filepath)
        return jsonify({
            'session_file': f"{session_id}_{filename}",
            'dados_extraidos': dados
        }), 200

    except Exception as e:
        return jsonify({'error': f'Erro ao processar PDF: {str(e)}'}), 500
