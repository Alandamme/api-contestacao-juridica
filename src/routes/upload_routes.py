from flask import Blueprint, request, jsonify
import fitz  # PyMuPDF

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/api/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo inválido'}), 400

    try:
        # Lê o conteúdo do PDF da memória
        pdf_bytes = file.read()
        if not pdf_bytes:
            return jsonify({'error': 'Arquivo enviado está vazio'}), 400

        doc = fitz.open(stream=pdf_bytes, filetype='pdf')

        texto = ""
        for page in doc:
            texto += page.get_text()

        doc.close()

        return jsonify({
            'mensagem': 'PDF processado com sucesso',
            'trecho': texto[:1000]
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Falha ao processar o PDF',
            'details': str(e)
        }), 500

