from flask import Blueprint, request, jsonify
import os
import json
import uuid
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF

from src.utils.ContestacaoIAGenerator import ContestacaoIAGenerator
from src.utils.document_generator import DocumentGenerator

# ✅ Define o blueprint
contestacao_bp = Blueprint('contestacao', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 📄 ROTA 1 - UPLOAD DE PETIÇÃO INICIAL
@contestacao_bp.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome do arquivo vazio'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        session_id = str(uuid.uuid4())
        session_dir = os.path.join('uploads', session_id)
        os.makedirs(session_dir, exist_ok=True)

        filepath = os.path.join(session_dir, filename)
        file.save(filepath)

        # Extrai texto do PDF
        texto = ''
        with fitz.open(filepath) as doc:
            for page in doc:
                texto += page.get_text()

        # Monta JSON de sessão com estrutura básica
        dados = {
