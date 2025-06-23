from flask import Blueprint, request, jsonify

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/api/upload', methods=['POST'])
def upload_file():
    # Verifica se o arquivo foi enviado
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo inválido'}), 400

    # Aqui você pode salvar ou processar o arquivo como quiser
    # Exemplo: file.save('/tmp/' + file.filename)

    return jsonify({'message': f'Arquivo "{file.filename}" recebido com sucesso!'}), 200
