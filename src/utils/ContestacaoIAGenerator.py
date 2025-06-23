import os
import json
from typing import Dict
from openai import OpenAI


class ContestacaoIAGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Inicializa o gerador com a chave da API e o modelo desejado.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def gerar_argumentacao_ia(self, entrada_usuario: str) -> Dict[str, str]:
        """
        Usa a IA para gerar argumentos jurídicos com base na petição inicial.
        """
        prompt = (
            "Você é um advogado especialista em contestações. Com base na petição inicial abaixo, gere os seguintes argumentos jurídicos:\n\n"
            "- argumento_preliminar\n"
            "- argumento_esclarecimentos_iniciais\n"
            "- argumento_conduta_empresa\n"
            "- argumento_cumprimento_contrato\n"
            "- argumento_cdc\n"
            "- argumento_onus_prova\n"
            "- pedidos_finais\n\n"
            f"Petição inicial:\n{entrada_usuario}\n\n"
            "Responda em formato JSON, com cada um dos campos como chave."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            conteudo = response.choices[0].message.content
            return json.loads(conteudo)
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar argumentos com IA: {e}")

    def gerar_dados_para_modelo(self, dados_fixos: Dict[str, str], texto_peticao: str) -> Dict[str, str]:
        """
        Gera todos os dados finais (fixos + IA) que serão usados no preenchimento do modelo.
        """
        argumentos_ia = self.gerar_argumentacao_ia(texto_peticao)
        return {**dados_fixos, **argumentos_ia}
