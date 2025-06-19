import openai

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

    def gerar_contestacao(self, dados_processo: str) -> str:
        """
        Gera a contestação com base no conteúdo do modelo e os dados fornecidos do processo.
        """
        prompt_base = self.carregar_modelo_padrao()
        prompt = f"{prompt_base}\n\nINFORMAÇÕES DO PROCESSO:\n{dados_processo}"

        try:
            resposta = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            return resposta.choices[0].message["content"]
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar contestação com IA: {e}")
