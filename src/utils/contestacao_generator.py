import openai
import os
import json

class ContestacaoGenerator:
    # ... mantenha os outros métodos e __init__ como estão ...

    def generate_contestacao(self, dados_extraidos: dict, dados_reu: dict = None) -> str:
        """
        Gera uma contestação usando IA com base no modelo padrão e nos dados extraídos
        """
        # Caminho do modelo padrão (ajuste se necessário!)
        modelo_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'static', 'modelos', 'contestacao_padrao.txt'
        )
        modelo_path = os.path.abspath(modelo_path)

        with open(modelo_path, 'r', encoding='utf-8') as f:
            modelo = f.read()

        # Novo prompt aprimorado
        prompt = f"""
Você é um advogado especialista em contestação judicial.

Sua tarefa é gerar uma contestação completa e personalizada com base:

1. Nos dados extraídos do PDF da petição inicial;
2. Nos dados do réu fornecidos (quando houver);
3. No modelo padrão do escritório.

Regras:
- Substitua todos os campos do modelo (como {{autor}}, {{reu}}, {{processo}}, {{valor_causa}}, {{fatos}}, etc) com os dados extraídos.
- Se um campo estiver ausente, deixe "[DADO NÃO ENCONTRADO]".
- Use o máximo possível dos fatos e pedidos do caso real.
- A peça deve ser pronta para uso jurídico, em linguagem técnica.

MODELO PADRÃO:
{modelo}

DADOS EXTRAÍDOS DO PDF:
{json.dumps(dados_extraidos, ensure_ascii=False, indent=2)}

DADOS DO RÉU (opcionais):
{json.dumps(dados_reu, ensure_ascii=False, indent=2) if dados_reu else '[Não fornecido]'}
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
