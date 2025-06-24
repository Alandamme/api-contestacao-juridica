from flask import Blueprint, request, jsonify
import os
import json
import uuid
from werkzeug.utils import secure_filename
from src.utils.pdf_processor import PDFProcessor
from src.utils.contestacao_generator import gerar_contestacao_ia_formatada

contestacao_bp = Blueprint('contestacao', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 📄 1. Upload da Petição Inicial
@contestacao_bp.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nome de arquivo inválido'}), 400

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Formato inválido. Envie um arquivo PDF.'}), 400

        # Salva o PDF no diretório temporário
        temp_path = f"/tmp/{file.filename}"
        file.save(temp_path)

        # Processa com IA
        processor = PDFProcessor()
        dados = processor.process_pdf(temp_path)

        return jsonify({
            'mensagem': 'Petição processada com sucesso',
            'dados_extraidos': dados
        }), 200

    except Exception as e:
        # Loga no terminal da Render
        print(f"[ERRO] upload_pdf(): {e}")
        return jsonify({'error': f"Erro ao processar PDF: {str(e)}"}), 500
