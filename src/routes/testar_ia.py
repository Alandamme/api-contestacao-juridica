import os
from flask import Blueprint, request, jsonify
from openai import OpenAI

testar_ia_bp = Blueprint("testar_ia", __name__)
client = OpenAI()

@testar_ia_bp.route("/testar-ia", methods=["POST"])
def testar_ia():
    data = request.json
    if not data:
        return jsonify({"erro": "JSON ausente"}), 400

    dados_peticao = data.get("session_file")
    if not dados_peticao:
        return jsonify({"erro": "Dados da petição ausentes"}), 400

    try:
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

        stream = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um advogado especializado em direito civil, especialista em petições."},
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

        return jsonify({
            "mensagem": "Pré-visualização gerada com sucesso!",
            "corpo_gerado": corpo_gerado
        }), 200

    except Exception as e:
        print(f"Erro ao gerar prévia com IA: {e}")
        return jsonify({"erro": f"Erro ao gerar texto com IA: {str(e)}"}), 500

