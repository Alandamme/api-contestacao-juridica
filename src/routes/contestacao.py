import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from docx import Document
from datetime import datetime
from src.utils.pdf_processor import PDFProcessor
from openai import OpenAI

contestacao_bp = Blueprint("contestacao", __name__)
pdf_processor = PDFProcessor()

# Diretórios
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
MODELO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "modelos", "modelo_contestacao_com_placeholders_pronto.docx"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@contestacao_bp.route("/gerar-contestacao", methods=["POST"])
def gerar_contestacao():
    data = request.json
    if not data:
        return jsonify({"erro": "JSON ausente"}), 400

    dados_peticao = data.get("session_file")
    dados_advogado = data.get("dados_advogado")

    if not dados_peticao or not dados_advogado:
        return jsonify({"erro": "Dados incompletos para gerar contestacao"}), 400

    try:
        prompt = f"""
        Elabore uma contestacao juridica completa, clara e tecnica, baseada nos elementos abaixo extraidos da peticao inicial:

        Autor: {dados_peticao.get("autor", "nao identificado")}
        Reu: {dados_peticao.get("reu", "nao identificado")}
        Tipo de Acao: {dados_peticao.get("tipo_acao", "")}
        Valor da Causa: {dados_peticao.get("valor_causa", "")}

        Fatos alegados pelo autor:
        {dados_peticao.get("fatos", "")}

        Pedidos do autor:
        {dados_peticao.get("pedidos", [])}

        Fundamentos juridicos apresentados pelo autor:
        {dados_peticao.get("fundamentos_juridicos", [])}

        Responda ponto a ponto, rebatendo cada argumento com base no direito civil atual, com linguagem tecnica e moderna, sem inventar jurisprudencia.
        """

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Voce e um advogado civilista, especialista em redigir contestacoes tecnicas e atuais."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=1000
        )

        corpo_gerado = response.choices[0].message.content

        # Gerar Word
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

        def substituir_placeholder(paragraph, key, value):
            if key in paragraph.text:
                for run in paragraph.runs:
                    if key in run.text:
                        run.text = run.text.replace(key, value)

        for paragraph in doc.paragraphs:
            for key, value in placeholders.items():
                substituir_placeholder(paragraph, key, value)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"contestacao_{timestamp}.docx"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        doc.save(output_path)

        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        print(f"Erro ao gerar contestacao: {e}")
        return jsonify({"erro": f"Erro ao gerar contestacao: {str(e)}"}), 500



