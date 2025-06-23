from flask import Blueprint, request, jsonify
import os
import json
import uuid
from werkzeug.utils import secure_filename
from src.utils.pdf_processor import PDFProcessor
from src.utils.contestacao_generator import ContestacaoGenerator

contestacao_bp = Blueprint('contestacao', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 📄 1. Upload da Petição Inicial
@contestacao_bp.route('/api/upload', methods=['POST'])
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

        try:
            processor = PDFProcessor()
            dados = processor.process_pdf(filepath)
        except Exception as e:
            return jsonify({'error': f'Erro ao processar PDF: {str(e)}'}), 500

        session_file = os.path.join(session_dir, 'session.json')
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

        return jsonify({
            'message': 'Petição inicial processada com sucesso',
            'session_file': session_file,
            'dados_extraidos': dados
        }), 200

    return jsonify({'error': 'Arquivo inválido. Envie um PDF.'}), 400


# ⚖️ 2. Gerar Contestação com IA Jurídica (única opção)
@contestacao_bp.route('/api/gerar-contestacao', methods=['POST'])
def gerar_contestacao():
    try:
        data = request.get_json()
        if not data or 'session_file' not in data:
            return jsonify({'error': 'session_file ausente'}), 400

        session_file = data['session_file']
        if not os.path.exists(session_file):
            return jsonify({'error': 'Arquivo de sessão não encontrado'}), 404

        with open(session_file, 'r', encoding='utf-8') as f:
            dados_extraidos = json.load(f)

        dados_reu = data.get('dados_reu', {})
        generator = ContestacaoGenerator()
        contestacao_id, word_path, preview = generator.gerar_documento(dados_extraidos, dados_reu)

        return jsonify({
            'message': 'Contestação gerada com sucesso',
            'contestacao_id': contestacao_id,
            'preview': preview,
            'files': {
                'word': word_path
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'Erro ao gerar contestação: {str(e)}'}), 500
