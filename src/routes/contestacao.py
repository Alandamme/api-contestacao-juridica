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
            'fatos': texto,
            'tipo_acao': 'Ação Cível (placeholder)',
            'valor_causa': 'R$ 0,00 (placeholder)',
            'autor': {'nome': 'Autor Desconhecido'},
            'reu': {'nome': 'Réu Desconhecido'},
        }

        session_path = os.path.join(session_dir, 'session.json')
        with open(session_path, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

        return jsonify({
            'message': 'Petição inicial processada com sucesso',
            'session_file': session_path,
            'preview': texto[:1000] + '...'
        })

    return jsonify({'error': 'Arquivo não permitido. Envie um PDF.'}), 400


# ⚖️ ROTA 2 - GERAÇÃO DA CONTESTAÇÃO AVANÇADA
@contestacao_bp.route('/gerar-contestacao-ia-avancada', methods=['POST'])
def gerar_contestacao_ia_avancada():
    try:
        data = request.get_json()
        if not data or 'session_file' not in data:
            return jsonify({'error': 'Dados da sessão não fornecidos'}), 400

        session_file = data['session_file']
        if not os.path.exists(session_file):
            return jsonify({'error': 'Sessão expirada ou inválida'}), 400

        with open(session_file, 'r', encoding='utf-8') as f:
            dados_extraidos = json.load(f)

        dados_reu = data.get('dados_reu', {})

        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            return jsonify({'error': 'OPENAI_API_KEY não configurada no ambiente'}), 500

        # Inicializa gerador com IA
        ia_generator = ContestacaoIAGenerator(api_key=OPENAI_API_KEY)

        # Gera argumentos jurídicos com IA
        argumentos_ia = ia_generator.gerar_argume_
