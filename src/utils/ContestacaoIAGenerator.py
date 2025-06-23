from openai import OpenAI
from typing import Dict
import os
import json

class ContestacaoIAGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Inicializa o gerador com a chave da API e o modelo desejado.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def carregar_modelo_padrao(self, caminho_arquivo: str = "src/utils/contestacao_padrao.txt") -> str:
        """
        Carrega o conteúdo base do prompt a partir de um arquivo.
        """
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
        with open(caminho_arquivo, "r", encoding="utf-8") as file:
            return file.read()

    def preencher_placeholders(self, modelo: str, dados: Dict[str, str]) -> str:
        """
        Substitui os placeholders do modelo com os dados fornecidos.
        """
        for chave, valor in dados.items():
            modelo = modelo.replace(f"{{{{{chave}}}}}", valor.strip())
        return modelo

    def gerar_argumentacao_ia(self, entrada_usuario: str) -> Dict[str, str]:
        """
        Usa a IA para gerar argumentos jurídicos com base na petição inicial.
        """
        prompt = (
            "Você é um advogado especializado em contestações. Com base na petição inicial a seguir, gere os blocos argumentativos abaixo:\n\n"
            "- argumento_preliminar\n"
            "- argumento_esclarecimentos_iniciais\n"
            "- argumento_conduta_empresa\n"
            "- argumento_cumprimento_contrato\n"
            "- argumento_cdc\n"
            "- argumento_onus_prova\n"
            "- pedidos_finais\n\n"
            f"Texto da petição inicial:\n{entrada_usuario}\n\n"
            "Responda em formato JSON com os campos listados."
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

    def gerar_contestacao(self, dados_fixos: Dict[str, str], texto_inicial: str) -> str:
        """
        Gera a contestação final: combina dados fixos e argumentos da IA no modelo base.
        """
        modelo_base = self.carregar_modelo_padrao()
        argumentos_ia = self.gerar_argumentacao_ia(texto_inicial)
        dados_completos = {**dados_fixos, **argumentos_ia}
        return self.preencher_placeholders(modelo_base, dados_completos)
