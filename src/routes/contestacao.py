from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
import json

from src.utils.pdf_processor import PDFProcessor
from src.utils.contestacao_generator import ContestacaoGenerator
from src.utils.document_generator import DocumentGenerator

contestacao_bp = Blueprint('contestacao', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Health check/teste
@contestacao_bp.route('/teste', methods=['GET'])
def teste():
    return jsonify({"status": "Contestacao blueprint funcionando!"})

# 1. Upload de petição inicial em PDF
@contestacao_bp.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo foi enviado'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)

            # Processa PDF e extrai dados
            processor = PDFProcessor()
            dados_extraidos = processor.process_pdf(file_path)

            # Warnings
            warnings = []
            if not dados_extraidos.get('autor'):
                warnings.append("Autor não identificado claramente")
            if not dados_extraidos.get('reu'):
                warnings.append("Réu não identificado claramente")
            if not dados_extraidos.get('pedidos') or len(dados_extraidos.get('pedidos', [])) == 0:
                warnings.append("Nenhum pedido específico identificado")

            # Salva dados em sessão temporária
            session_file = os.path.join(temp_dir, 'dados_extraidos.json')
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(dados_extraidos, f, ensure_ascii=False, indent=2)

            return jsonify({
                'message': 'Arquivo processado com sucesso',
                'filename': filename,
                'file_path': file_path,
                'session_file': session_file,
                'dados_extraidos': {
                    'tipo_acao': dados_extraidos.get('tipo_acao'),
                    'valor_causa': dados_extraidos.get('valor_causa'),
                    'autor': dados_extraidos.get('autor'),
                    'reu': dados_extraidos.get('reu'),
                    'fatos': dados_extraidos.get('fatos'),
                    'pedidos': dados_extraidos.get('pedidos'),
                    'fundamentos_juridicos': dados_extraidos.get('fundamentos_juridicos')
                },
                'pedidos_count': len(dados_extraidos.get('pedidos', [])),
                'warnings': warnings
            }), 200

        except Exception as e:
            return jsonify({'error': f'Erro no processamento: {str(e)}'}), 500

    return jsonify({'error': 'Tipo de arquivo não permitido. Apenas PDFs são aceitos.'}), 400

# 2. Gerar contestação
@contestacao_bp.route('/generate-contestacao', methods=['POST'])
def generate_contestacao():
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

        # IA gera contestação
        generator = ContestacaoGenerator()
        contestacao_text = generator.generate_contestacao(dados_extraidos, dados_reu)

        # Gera arquivos (txt, word, pdf)
        doc_generator = DocumentGenerator()
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
        os.makedirs(output_dir, exist_ok=True)

        txt_filename = f'contestacao_{unique_id}.txt'
        word_filename = f'contestacao_{unique_id}.docx'
        pdf_filename = f'contestacao_{unique_id}.pdf'
        txt_path = os.path.join(output_dir, txt_filename)
        word_path = os.path.join(output_dir, word_filename)
        pdf_path = os.path.join(output_dir, pdf_filename)

        # Salva arquivos
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(contestacao_text)
        doc_generator.create_word_document(contestacao_text, word_path)
        doc_generator.create_pdf_from_text(contestacao_text, pdf_path)

        return jsonify({
            'message': 'Contestação gerada com sucesso',
            'contestacao_id': unique_id,
            'files': {
                'txt': txt_path,
                'word': word_path,
                'pdf': pdf_path
            },
            'preview': contestacao_text[:700] + '...' if len(contestacao_text) > 700 else contestacao_text
        }), 200

    except Exception as e:
        return jsonify({'error': f'Erro na geração da contestação: {str(e)}'}), 500

# 3. Download dos arquivos
@contestacao_bp.route('/download/<file_type>/<contestacao_id>', methods=['GET'])
def download_contestacao(file_type, contestacao_id):
    try:
        if file_type not in ['txt', 'word', 'pdf']:
            return jsonify({'error': 'Tipo de arquivo inválido'}), 400

        extensions = {'txt': '.txt', 'word': '.docx', 'pdf': '.pdf'}
        extension = extensions[file_type]
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
        filename = f'contestacao_{contestacao_id}{extension}'
        file_path = os.path.join(output_dir, filename)

        if not os.path.exists(file_path):
            return jsonify({'error': 'Arquivo não encontrado'}), 404

        mimetypes = {
            'txt': 'text/plain',
            'word': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'pdf': 'application/pdf'
        }

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetypes[file_type]
        )

    except Exception as e:
        return jsonify({'error': f'Erro no download: {str(e)}'}), 500

# 4. Health check da API
@contestacao_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'API funcionando corretamente',
        'version': '1.0.0'
    }), 200
