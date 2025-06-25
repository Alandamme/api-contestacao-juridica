import os
from flask import Blueprint, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
from docx import Document
from datetime import datetime
import openai
from src.utils.pdf_processor import PDFProcessor

contestacao_bp = Blueprint("contestacao", __name__)
pdf_processor = PDFProcessor()

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define a chave da API da OpenAI a partir do ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")


# IA para gerar corpo da contestação
def gerar_corpo_contestacao_ia(dados_peticao):
    prompt = f"""
Você é um advogado especialista em direito cível.

Com base nas informações abaixo, redija uma CONTESTAÇÃO com estrutura jurídica formal, que inclua:
- Preliminares (se existirem)
- Defesa de mérito
- Impugnação dos pedidos do autor
- Fundamentos legais e doutrinários relevantes
- Estilo técnico, claro, conciso

DADOS EXTRAÍDOS DA PETIÇÃO:
Autor: {dados_peticao.get('autor', '')}
Réu: {dados_peticao.get('reu', '')}
Tipo de ação: {dados_peticao.get('tipo_acao', '')}
Valor da causa: {dados_peticao.get('valor_causa', '')}
Fatos: {dados_peticao.get('fatos', '')}
Pedidos: {dados_peticao.get('pedidos', '')}
Fundamentos jurídicos: {dados_peticao.get('fundamentos_juridicos', '')}

Escreva a contestação:
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2048
    )
    return response.choices[0].message.content.strip()


@contestacao_bp.route("/upload", methods=["POST"])
def upload_pdf():
    if "pdf" not in request.files:
        return jsonify({"erro": "Nenhum arquivo PDF enviado"}), 400

    file = request.files["pdf"]
    if file.filename == "":
        return jsonify({"erro": "Nome de arquivo inválido"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join("/tmp", filename)
    file.save(file_path)

    try:
        dados_extraidos = pdf_processor.process_pdf(file_path)
        return jsonify({"dados_extraidos": dados_extraidos, "session_file": dados_extraidos}), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao processar PDF: {str(e)}"}), 500


@contestacao_bp.route("/gerar-contestacao", methods=["POST"])
def gerar_contestacao():
    data = request.json
    if not data:
        return jsonify({"erro": "JSON ausente"}), 400

    dados_peticao = data.get("session_file")
    dados_advogado = data.get("dados_advogado")

    if not dados_peticao or not dados_advogado:
        return jsonify({"erro": "Dados incompletos para gerar contestação"}), 400

    try:
        # Gera o corpo da contestação com IA
        corpo_contestacao = gerar_corpo_contestacao_ia(dados_peticao)

        # Caminho para o modelo DOCX com placeholders
        modelo_path = os.path.join(os.path.dirname(__file__), "..", "static", "modelos", "modelo_contestacao_com_placeholders_pronto.docx")
        doc = Document(modelo_path)

        # Substituição dos campos
        campos = {
            "{{autor}}": dados_peticao.get("autor", ""),
            "{{reu}}": dados_peticao.get("reu", ""),
            "{{numero_processo}}": dados_peticao.get("numero_processo", "0000000-00.0000.0.00.0000"),
            "{{vara_comarca}}": dados_peticao.get("vara", "Vara Única da Comarca de ..."),
            "{{juiz_destino}}": "Excelentíssimo Senhor Doutor Juiz de Direito",
            "{{titulo_documento}}": "CONTESTAÇÃO",
            "{{corpo_contestacao}}": corpo_contestacao,
            "{{assinatura}}": f"{dados_advogado.get('nome_advogado', '')} – OAB/{dados_advogado.get('estado', '')} {dados_advogado.get('oab', '')}"
        }

        for p in doc.paragraphs:
            for key, val in campos.items():
                if key in p.text:
                    p.text = p.text.replace(key, val)

        # Salvar o novo arquivo gerado
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"contestacao_{timestamp}.docx"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        doc.save(output_path)

        return jsonify({
            "message": "Contestação gerada com sucesso!",
            "files": {
                "word": url_for("contestacao.download_file", filename=output_filename, _external=True)
            }
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao gerar contestação: {str(e)}"}), 500


@contestacao_bp.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    try:
        path = os.path.join(UPLOAD_FOLDER, filename)
        return send_file(path, as_attachment=True)
    except Exception as e:
        return jsonify({"erro": f"Erro ao baixar arquivo: {str(e)}"}), 500
