from flask import Blueprint, request, jsonify
from openai import OpenAI

testar_ia_bp = Blueprint("testar_ia", __name__)

@testar_ia_bp.route("/testar-ia", methods=["POST"])
def testar_ia():
    data = request.json
    dados_peticao = data.get("session_file")

    if not dados_peticao:
        return jsonify({"erro": "Dados da petição ausentes"}), 400

    try:
        # Converte listas em texto plano para o prompt
        pedidos = "; ".join(dados_peticao.get("pedidos", []))
        fundamentos = "; ".join(dados_peticao.get("fundamentos_juridicos", []))

        prompt = f"""
        Elabore uma contestação jurídica considerando os seguintes dados:

        - Autor: {dados_peticao.get("autor", "")}
        - Réu: {dados_peticao.get("reu", "")}
        - Tipo de Ação: {dados_peticao.get("tipo_acao", "")}
        - Valor da Causa: {dados_peticao.get("valor_causa", "")}

        Resumo dos Fatos:
        {dados_peticao.get("fatos", "")}

        Pedidos:
        {pedidos}

        Fundamentos Jurídicos:
        {fundamentos}

        Escreva a contestação com linguagem clara, coesa, técnica e argumentativa.
        """

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um advogado especialista em direito civil."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        texto = response.choices[0].message.content.strip()
        return jsonify({"corpo_gerado": texto}), 200

    except Exception as e:
        print("Erro ao gerar texto:", e)
        return jsonify({"erro": str(e)}), 500

