import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from src.utils.pdf_processor import PDFProcessor

upload_bp = Blueprint('upload_bp', __name__)

# Define pasta de upload
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Extensões permitidas
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo inválido.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não suportado. Envie um PDF.'}), 400

    filename = secure_filename(file.filename)
    session_id = str(uuid.uuid4())
    saved_filename = f"{session_id}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, saved_filename)

    try:
        file.save(filepath)
        processor = PDFProcessor()
        dados = processor.process_pdf(filepath)

        return jsonify({
            'session_file': saved_filename,
            'dados_extraidos': dados
        }), 200

    except Exception as e:
        return jsonify({'error': f'Erro ao processar PDF: {str(e)}'}), 500

