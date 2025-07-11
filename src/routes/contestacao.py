import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
from docxtpl import DocxTemplate
from src.utils.pdf_processor import PDFProcessor
from openai import OpenAI

contestacao_bp = Blueprint("contestacao", __name__)
pdf_processor = PDFProcessor()

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
MODELO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "modelos", "modelo_contestacao_com_placeholders_pronto.docx"))

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
        pedidos = "\n".join(dados_peticao.get("pedidos", []))
        fundamentos = "\n".join(dados_peticao.get("fundamentos_juridicos", []))

        prompt = f"""
        Elabore uma contestação jurídica completa, clara e técnica, baseada nos elementos abaixo extraídos da petição inicial:

        Autor: {dados_peticao.get("autor", "não identificado")}
        Réu: {dados_peticao.get("reu", "não identificado")}
        Tipo de Ação: {dados_peticao.get("tipo_acao", "")}
        Valor da Causa: {dados_peticao.get("valor_causa", "")}

        Fatos alegados pelo autor:
        {dados_peticao.get("fatos", "")}

        Pedidos do autor:
        {pedidos}

        Fundamentos jurídicos apresentados pelo autor:
        {fundamentos}

        Reponda ponto a ponto, rebatendo cada argumento com base no direito civil atual, com uma linguagem técnica e moderna, sem inventar jurisprudência.
        """

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um advogado civilista, especialista em redigir contestações técnicas e atuais."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1100,
            stream=False
        )

        corpo_gerado = response.choices[0].message.content.strip()

        doc = DocxTemplate(MODELO_PATH)
        doc.render({"corpo_contestacao": corpo_gerado})

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"contestacao_{timestamp}.docx"
        output_path = os.path.join("/tmp", output_filename)
        doc.save(output_path)

        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        print(f"Erro ao gerar contestação: {e}")
        return jsonify({"erro": str(e)}), 500


@contestacao_bp.route("/testar-ia-docx", methods=["POST"])
def testar_ia_gerar_word():
    data = request.json
    if not data:
        return jsonify({"erro": "JSON ausente"}), 400

    dados_peticao = data.get("session_file")
    if not dados_peticao:
        return jsonify({"erro": "Dados da petição ausentes"}), 400

    try:
        pedidos = "\n".join(dados_peticao.get("pedidos", []))
        fundamentos = "\n".join(dados_peticao.get("fundamentos_juridicos", []))

        prompt = f"""
        Elabore uma contestação jurídica completa, clara e técnica, baseada nos elementos abaixo extraídos da petição inicial:

        Autor: {dados_peticao.get("autor", "não identificado")}
        Réu: {dados_peticao.get("reu", "não identificado")}
        Tipo de Ação: {dados_peticao.get("tipo_acao", "")}
        Valor da Causa: {dados_peticao.get("valor_causa", "")}

        Fatos alegados pelo autor:
        {dados_peticao.get("fatos", "")}

        Pedidos do autor:
        {pedidos}

        Fundamentos jurídicos apresentados pelo autor:
        {fundamentos}

        Reponda ponto a ponto, rebatendo cada argumento com base no direito civil atual, com uma linguagem técnica e moderna, sem inventar jurisprudência.
        """

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um advogado civilista, especialista em redigir contestações técnicas e atuais."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1100,
            stream=False
        )

        corpo_gerado = response.choices[0].message.content.strip()

        doc = DocxTemplate(MODELO_PATH)
        doc.render({"corpo_contestacao": corpo_gerado})

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"contestacao_preview_{timestamp}.docx"
        output_path = os.path.join("/tmp", output_filename)
        doc.save(output_path)

        return jsonify({
            "corpo_contestacao": corpo_gerado,
            "arquivo_word": f"/download/{output_filename}"
        })

    except Exception as e:
        print(f"Erro ao testar IA e gerar Word: {e}")
        return jsonify({"erro": f"Erro ao testar IA e gerar Word: {str(e)}"}), 500


@contestacao_bp.route("/download/<filename>", methods=["GET"])
def baixar_arquivo(filename):
    caminho = os.path.join("/tmp", filename)
    if not os.path.isfile(caminho):
        return jsonify({"erro": "Arquivo não encontrado"}), 404
    return send_file(
        caminho,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

