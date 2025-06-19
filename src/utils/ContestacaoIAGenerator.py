import openai
from typing import Dict


class ContestacaoIAGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Inicializa o gerador de contestação com a chave da API e o modelo desejado.
        """
        openai.api_key = api_key
        self.model = model

    def carregar_modelo_padrao(self, caminho_arquivo: str = "src/utils/contestacao_padrao.txt") -> str:
        """
        Carrega o conteúdo base do prompt a partir de um arquivo de texto.
        """
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    def preencher_placeholders(self, modelo: str, dados: Dict[str, str]) -> str:
        """
        Substitui os placeholders do modelo com os dados fornecidos.
        """
        for chave, valor in dados.items():
            modelo = modelo.replace(f"{{{{{chave}}}}}", valor)
        return modelo

    def gerar_argumentacao_ia(self, entrada_usuario: str) -> Dict[str, str]:
        """
        Usa a IA para gerar trechos argumentativos jurídicos com base na petição inicial.
        """
        prompt = (
            "Você é um advogado especializado em contestações. "
            "A partir da petição inicial descrita abaixo, gere os seguintes trechos argumentativos jurídicos:\n\n"
            "- argumento_preliminar\n"
            "- argumento_esclarecimentos_iniciais\n"
            "- argumento_conduta_empresa\n"
            "- argumento_cumprimento_contrato\n"
            "- argumento_cdc\n"
            "- argumento_onus_prova\n\n"
            f"Texto da petição inicial:\n{entrada_usuario}\n\n"
            "Responda no formato JSON com os campos listados acima."
        )

        try:
            resposta = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            import json
            return json.loads(resposta.choices[0].message["content"])
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar argumentos jurídicos com IA: {e}")

    def gerar_contestacao(self, dados_fixos: Dict[str, str], texto_inicial: str) -> str:
        """
        Gera a contestação final: carrega o modelo, preenche com os dados fixos e gera os argumentos com IA.
        """
        modelo_base = self.carregar_modelo_padrao()
        argumentos_ia = self.gerar_argumentacao_ia(texto_inicial)

        # Combina os dados fixos com os gerados pela IA
        dados_completos = {**dados_fixos, **argumentos_ia}

        # Preenche o modelo com todos os campos
        return self.preencher_placeholders(modelo_base, dados_completos)
