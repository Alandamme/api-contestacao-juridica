import openai
import os
import json

class ContestacaoGenerator:
    # ... outros métodos ...

    def generate_contestacao(self, dados_extraidos: dict, dados_reu: dict = None) -> str:
        modelo_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'static', 'modelos', 'contestacao_padrao.txt'
        )
        modelo_path = os.path.abspath(modelo_path)

        with open(modelo_path, 'r', encoding='utf-8') as f:
            modelo = f.read()

        prompt = f"""
Você é um advogado especialista em contestações judiciais.
Use o modelo abaixo, substituindo todos os campos entre {{chaves}} com os dados extraídos da petição inicial (e dados do réu, se fornecidos).

Se algum campo não estiver disponível, escreva [DADO NÃO ENCONTRADO].

MODELO PADRÃO:
========================
{modelo}
========================

DADOS EXTRAÍDOS DO PDF:
{json.dumps(dados_extraidos, ensure_ascii=False, indent=2)}

DADOS DO RÉU (opcionais):
{json.dumps(dados_reu, ensure_ascii=False, indent=2) if dados_reu else '[Não fornecido]'}

Regras:
- Substitua todos os campos dinâmicos ({{autor}}, {{reu}}, {{vara}}, {{comarca}}, {{fatos}}, {{pedidos}}, etc).
- Mantenha a estrutura, formatação e argumentação jurídica do modelo.
- NÃO explique, apenas gere a peça completa, pronta para protocolo.
"""
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        resposta = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um advogado especialista em contestações jurídicas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3500,
            temperature=0.1
        )

        contestacao_text = resposta['choices'][0]['message']['content']
        return contestacao_text


