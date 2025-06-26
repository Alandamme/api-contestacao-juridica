import os
from flask import Blueprint, request, jsonify, url_for
from werkzeug.utils import secure_filename
from docx import Document
from datetime import datetime
from src.utils.pdf_processor import PDFProcessor
from openai import OpenAI

contestacao_bp = Blueprint("contestacao", __name__)
pdf_processor = PDFProcessor()

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
MODELO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "modelos", "modelo_contestacao_com_placeholders_pronto.docx")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
        print(f"Erro ao processar PDF: {e}")
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
        # Etapa 1: Geração do corpo com IA jurídica (OpenAI GPT)
        prompt = f"""
        Elabore uma contestação jurídica completa, considerando os seguintes elementos extraídos da petição inicial:

        - Autor: {dados_peticao.get("autor", "")}
        - Réu: {dados_peticao.get("reu", "")}
        - Tipo de Ação: {dados_peticao.get("tipo_acao", "")}
        - Valor da Causa: {dados_peticao.get("valor_causa", "")}

        Resumo dos fatos:
        {dados_peticao.get("fatos", "")}

        Pedidos do autor:
        {dados_peticao.get("pedidos", [])}

        Fundamentos jurídicos apresentados:
        {dados_peticao.get("fundamentos_juridicos", [])}

        Gere uma contestação técnica, clara e fundamentada com base nessas informações.
        """

        client = OpenAI()

        # Sem streaming para evitar estouro de memória
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um advogado especializado em direito civil, especialista em petições."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            stream=False
        )

        corpo_gerado = completion.choices[0].message.content.strip()

        # Etapa 2: Substituição no modelo Word
        doc = Document(MODELO_PATH)

        placeholders = {
            "{{AUTOR}}": dados_peticao.get("autor", ""),
            "{{REU}}": dados_peticao.get("reu", ""),
            "{{TIPO_ACAO}}": dados_peticao.get("tipo_acao", ""),
            "{{VALOR_CAUSA}}": dados_peticao.get("valor_causa", ""),
            "{{RESUMO_FATOS}}": dados_peticao.get("fatos", ""),
            "{{PEDIDOS}}": "\n".join(f"- {p}" for p in dados_peticao.get("pedidos", [])),
            "{{FUNDAMENTOS_JURIDICOS}}": "\n".join(f"- {f}" for f in dados_peticao.get("fundamentos_juridicos", [])),
            "{{NOME_ADVOGADO}}": dados_advogado.get("nome_advogado", ""),
            "{{OAB}}": dados_advogado.get("oab", ""),
            "{{ESTADO}}": dados_advogado.get("estado", ""),
            "{{CONTESTACAO_IA}}": corpo_gerado
        }

        for paragraph in doc.paragraphs:
            for key, value in placeholders.items():
                if key in paragraph.text:
                    paragraph.text = paragraph.text.replace(key, value)

        # Salvar a versão final
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"contestacao_{timestamp}.docx"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        doc.save(output_path)

        return jsonify({
            "message": "Contestação gerada com sucesso!",
            "files": {
                "word": url_for("download_file", filename=output_filename, _external=True)
            }
        }), 200

    except Exception as e:
        print(f"Erro ao gerar contestação: {e}")
        return jsonify({"erro": f"Erro ao gerar contestação: {str(e)}"}), 500

