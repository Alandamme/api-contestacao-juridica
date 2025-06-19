from src.utils.ContestacaoIAGenerator import ContestacaoIAGenerator
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
import json
import uuid

from src.utils.pdf_processor import PDFProcessor
from src.utils.contestacao_generator import ContestacaoGenerator
from src.utils.document_generator import DocumentGenerator

contestacao_bp = Blueprint('contestacao', __name__)
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 0. Health check/teste
@contestacao_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'API funcionando corretamente',
        'version': '1.0.0'
    }), 200

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

            processor = PDFProcessor()
            dados_extraidos = processor.process_pdf(file_path)

            warnings = []
            if not dados_extraidos.get('autor'):
                warnings.append("Autor não identificado claramente")
            if not dados_extraidos.get('reu'):
                warnings.append("Réu não identificado claramente")
            if not dados_extraidos.get('pedidos') or len(dados_extraidos.get('pedidos', [])) == 0:
                warnings.append("Nenhum pedido específico identificado")

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

# 2. Geração padrão (sem IA com modelo)
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

        generator = ContestacaoGenerator()
        contestacao_text = generator.generate_contestacao(dados_extraidos, dados_reu)

        unique_id = str(uuid.uuid4())[:8]
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
        os.makedirs(output_dir, exist_ok=True)

        txt_path = os.path.join(output_dir, f'contestacao_{unique_id}.txt')
        word_path = os.path.join(output_dir, f'contestacao_{unique_id}.docx')
        pdf_path = os.path.join(output_dir, f'contestacao_{unique_id}.pdf')

        doc_generator = DocumentGenerator()
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

# 3. Geração via IA com modelo do escritório
@contestacao_bp.route('/gerar-contestacao-ia', methods=['POST'])
def gerar_contestacao_ia():
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

        modelo_path = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'modelos', 'contestacao_padrao.txt')
        if not os.path.exists(modelo_path):
            return jsonify({'error': 'Modelo do escritório não encontrado.'}), 500

        with open(modelo_path, 'r', encoding='utf-8') as f:
            modelo_padrao = f.read()

        generator = ContestacaoGenerator()
        contestacao_text = generator.generate_contestacao_custom(dados_extraidos, dados_reu, modelo_padrao)

        unique_id = str(uuid.uuid4())[:8]
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
        os.makedirs(output_dir, exist_ok=True)

        txt_path = os.path.join(output_dir, f'contestacao_{unique_id}.txt')
        word_path = os.path.join(output_dir, f'contestacao_{unique_id}.docx')
        pdf_path = os.path.join(output_dir, f'contestacao_{unique_id}.pdf')

        doc_generator = DocumentGenerator()
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(contestacao_text)
        doc_generator.create_word_document(contestacao_text, word_path)
        doc_generator.create_pdf_from_text(contestacao_text, pdf_path)

        return jsonify({
            'message': 'Contestação (IA + modelo do escritório) gerada com sucesso',
            'contestacao_id': unique_id,
            'files': {
                'txt': txt_path,
                'word': word_path,
                'pdf': pdf_path
            },
            'preview': contestacao_text[:700] + '...' if len(contestacao_text) > 700 else contestacao_text
        }), 200

    except Exception as e:
        return jsonify({'error': f'Erro na geração da contestação com IA: {str(e)}'}), 500

# 4. Download de arquivos
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

# 5. Debug: Listar arquivos do diretório de modelos
@contestacao_bp.route('/debug/lista-arquivos', methods=['GET'])
def debug_lista_arquivos():
    caminho = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'modelos'))
    arquivos = os.listdir(caminho) if os.path.exists(caminho) else []
    return jsonify({
        "caminho": caminho,
        "arquivos": arquivos
    })

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

        # Inicializa IA Generator com API Key do ambiente
       
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    return jsonify({'error': 'OPENAI_API_KEY não configurada no ambiente'}), 500

ia_generator = ContestacaoIAGenerator(api_key=OPENAI_API_KEY)


        # Gera texto de contestação com placeholders + argumentos gerados via IA
        contestacao_text = ia_generator.gerar_contestacao(dados_reu, dados_extraidos.get('fatos', ''))

        # Salva arquivos nos formatos desejados
        unique_id = str(uuid.uuid4())[:8]
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
        os.makedirs(output_dir, exist_ok=True)

        txt_path = os.path.join(output_dir, f'contestacao_{unique_id}.txt')
        word_path = os.path.join(output_dir, f'contestacao_{unique_id}.docx')
        pdf_path = os.path.join(output_dir, f'contestacao_{unique_id}.pdf')

        doc_generator = DocumentGenerator()
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(contestacao_text)
        doc_generator.create_word_document(contestacao_text, word_path)
        doc_generator.create_pdf_from_text(contestacao_text, pdf_path)

        return jsonify({
            'message': 'Contestação com placeholders + IA gerada com sucesso',
            'contestacao_id': unique_id,
            'files': {
                'txt': txt_path,
                'word': word_path,
                'pdf': pdf_path
            },
            'preview': contestacao_text[:700] + '...' if len(contestacao_text) > 700 else contestacao_text
        }), 200

    except Exception as e:
        return jsonify({'error': f'Erro na geração avançada com IA: {str(e)}'}), 500
