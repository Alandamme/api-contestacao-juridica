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
        Você é um advogado cível especialista em elaboração de contestações.

        Com base nos dados extraídos da petição inicial abaixo, redija uma contestação completa, organizada por tópicos. Refaça ponto a ponto os argumentos trazidos pelo autor, rebatendo com fundamentos jurídicos sólidos, técnicos e atuais, sem inventar jurisprudência.

        - Autor: {dados_peticao.get("autor", "NOME DO AUTOR NÃO DETECTADO")}
        - Réu: {dados_peticao.get("reu", "NOME DO RÉU NÃO DETECTADO")}
        - Tipo de Ação: {dados_peticao.get("tipo_acao", "")}
        - Valor da Causa: {dados_peticao.get("valor_causa", "")}

        Resumo dos fatos (segundo o autor):
        {dados_peticao.get("fatos", "")}

        Pedidos do autor:
        {dados_peticao.get("pedidos", [])}

        Fundamentos jurídicos alegados pelo autor:
        {dados_peticao.get("fundamentos_juridicos", [])}

        Estruture sua resposta da seguinte forma:
        1. Breve Síntese da Petição Inicial
        2. Preliminares (se houver)
        3. Impugnação dos Fatos
        4. Impugnação dos Fundamentos Jurídicos
        5. Direito Aplicável ao Caso
        6. Pedido Final de Improcedência
        7. Requerimentos

        Seja claro, técnico e preciso, utilizando linguagem jurídica atual e objetiva.
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


