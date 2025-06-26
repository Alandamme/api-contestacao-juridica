# src/routes/testar_ia.py
import os
from flask import Blueprint, request, jsonify
from openai import OpenAI
from src.utils.pdf_processor import PDFProcessor

MODELO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "modelos", "modelo_contestacao_com_placeholders_pronto.docx")

pdf_processor = PDFProcessor()
testar_ia_bp = Blueprint("testar_ia", __name__)

@testar_ia_bp.route("/testar-ia", methods=["POST"])
def testar_ia():
    data = request.json
    if not data:
        return jsonify({"erro": "JSON ausente"}), 400

    dados_peticao = data.get("session_file")
    dados_advogado = data.get("dados_advogado")

    if not dados_peticao or not dados_advogado:
        return jsonify({"erro": "Dados incompletos para testar IA"}), 400

    try:
        prompt = f"""
        Elabore uma contestacao juridica completa, considerando os seguintes elementos extraidos da peticao inicial:

        - Autor: {dados_peticao.get("autor", "")}
        - Reu: {dados_peticao.get("reu", "")}
        - Tipo de Acao: {dados_peticao.get("tipo_acao", "")}
        - Valor da Causa: {dados_peticao.get("valor_causa", "")}

        Resumo dos fatos:
        {dados_peticao.get("fatos", "")}

        Pedidos do autor:
        {dados_peticao.get("pedidos", [])}

        Fundamentos juridicos apresentados:
        {dados_peticao.get("fundamentos_juridicos", [])}

        Gere uma contestacao tecnica, clara e fundamentada com base nessas informacoes.
        """

        client = OpenAI()
        stream = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Voce e um advogado especializado em direito civil, especialista em peticoes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            stream=True
        )

        corpo_gerado = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                corpo_gerado += chunk.choices[0].delta.content

        return jsonify({"corpo_gerado": corpo_gerado}), 200

    except Exception as e:
        print(f"Erro ao gerar corpo com IA: {e}")
        return jsonify({"erro": f"Erro ao gerar corpo com IA: {str(e)}"}), 500
