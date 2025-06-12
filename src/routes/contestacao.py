from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
import json
from src.utils.pdf_processor import PDFProcessor
from src.utils.validator import PDFValidator
from src.utils.contestacao_generator import ContestacaoGenerator
from src.utils.document_generator import DocumentGenerator

contestacao_bp = Blueprint('contestacao', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@contestacao_bp.route('/upload', methods=['POST'])
def upload_pdf():
    """
    Endpoint para upload e processamento de petição inicial em PDF
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo foi enviado'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            
            # Salvar temporariamente o arquivo
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            
            # Validar arquivo PDF
            validator = PDFValidator()
            is_valid, message = validator.validate_pdf_file(file_path)
            
            if not is_valid:
                return jsonify({'error': f'Arquivo inválido: {message}'}), 400
            
            # Processar PDF
            processor = PDFProcessor()
            dados_extraidos = processor.process_pdf(file_path)
            
            # Validar dados extraídos
            data_valid, warnings = validator.validate_extracted_data(dados_extraidos)
            
            # Salvar dados em sessão (simulado com arquivo temporário)
            session_file = os.path.join(temp_dir, 'dados_extraidos.json')
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(dados_extraidos, f, ensure_ascii=False, indent=2)
            
            return jsonify({
                'message': 'Arquivo processado com sucesso',
                'filename': filename,
                'file_path': file_path,
                'session_file': session_file,
                'dados_extraidos': {
                    'partes': dados_extraidos.get('partes'),
                    'tipo_acao': dados_extraidos.get('tipo_acao'),
                    'valor_causa': dados_extraidos.get('valor_causa'),
                    'pedidos_count': len(dados_extraidos.get('pedidos', [])),
                    'fundamentos_juridicos': dados_extraidos.get('fundamentos_juridicos')
                },
                'data_valid': data_valid,
                'warnings': warnings
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Erro no processamento: {str(e)}'}), 500
    
    return jsonify({'error': 'Tipo de arquivo não permitido. Apenas PDFs são aceitos.'}), 400

@contestacao_bp.route('/generate-contestacao', methods=['POST'])
def generate_contestacao():
    """
    Endpoint para gerar contestação a partir dos dados processados
    """
    try:
        data = request.get_json()
        
        if not data or 'session_file' not in data:
            return jsonify({'error': 'Dados da sessão não fornecidos'}), 400
        
        session_file = data['session_file']
        
        if not os.path.exists(session_file):
            return jsonify({'error': 'Sessão expirada ou inválida'}), 400
        
        # Carregar dados extraídos
        with open(session_file, 'r', encoding='utf-8') as f:
            dados_extraidos = json.load(f)
        
        # Dados opcionais do réu
        dados_reu = data.get('dados_reu', {})
        
        # Gerar contestação
        generator = ContestacaoGenerator()
        contestacao_text = generator.generate_contestacao(dados_extraidos, dados_reu)
        
        # Gerar documentos
        doc_generator = DocumentGenerator()
        
        # Criar nomes únicos para os arquivos
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # Salvar em diferentes formatos
        txt_filename = f'contestacao_{unique_id}.txt'
        word_filename = f'contestacao_{unique_id}.docx'
        pdf_filename = f'contestacao_{unique_id}.pdf'
        
        txt_path = generator.save_contestacao_to_file(contestacao_text, txt_filename)
        word_path = doc_generator.create_word_document(contestacao_text, word_filename)
        pdf_path = doc_generator.create_pdf_from_text(contestacao_text, pdf_filename)
        
        return jsonify({
            'message': 'Contestação gerada com sucesso',
            'contestacao_id': unique_id,
            'files': {
                'txt': txt_path,
                'word': word_path,
                'pdf': pdf_path
            },
            'preview': contestacao_text[:500] + '...' if len(contestacao_text) > 500 else contestacao_text
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro na geração da contestação: {str(e)}'}), 500

@contestacao_bp.route('/download/<file_type>/<contestacao_id>', methods=['GET'])
def download_contestacao(file_type, contestacao_id):
    """
    Endpoint para download dos documentos gerados
    """
    try:
        # Validar tipo de arquivo
        if file_type not in ['txt', 'word', 'pdf']:
            return jsonify({'error': 'Tipo de arquivo inválido'}), 400
        
        # Determinar extensão
        extensions = {'txt': '.txt', 'word': '.docx', 'pdf': '.pdf'}
        extension = extensions[file_type]
        
        # Construir caminho do arquivo
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
        filename = f'contestacao_{contestacao_id}{extension}'
        file_path = os.path.join(output_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # Determinar mimetype
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

@contestacao_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar se a API está funcionando
    """
    return jsonify({
        'status': 'API funcionando corretamente',
        'version': '1.0.0',
        'endpoints': [
            '/api/upload - POST - Upload de petição inicial em PDF',
            '/api/generate-contestacao - POST - Geração de contestação',
            '/api/download/<type>/<id> - GET - Download de documentos',
            '/api/health - GET - Status da API'
        ]
    }), 200

