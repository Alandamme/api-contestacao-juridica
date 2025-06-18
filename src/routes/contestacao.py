from flask import Blueprint, request, jsonify, send_file
import os
import json
import tempfile

# Importe as suas classes utilitárias conforme for usar
# from src.utils.pdf_processor import PDFProcessor
# from src.utils.contestacao_generator import ContestacaoGenerator
# from src.utils.document_generator import DocumentGenerator

contestacao_bp = Blueprint('contestacao', __name__)

@contestacao_bp.route('/api/contestacao/teste', methods=['GET'])
def teste():
    return jsonify({"status": "Contestacao blueprint funcionando!"})

# Aqui você vai colocar as outras rotas reais, como upload, generate-contestacao, download, etc.
# Exemplo:
#
# @contestacao_bp.route('/api/upload', methods=['POST'])
# def upload_pdf():
#     # Sua lógica...
#     return jsonify({"msg": "Arquivo recebido!"})

