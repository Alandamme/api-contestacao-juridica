"""
Módulo de validação para processamento de PDFs jurídicos e dados de advogado
"""

import os
from typing import Dict, List, Tuple


class PDFValidator:
    """
    Classe responsável por validar PDFs e dados extraídos
    """

    @staticmethod
    def validate_pdf_file(file_path: str) -> Tuple[bool, str]:
        """
        Valida se o arquivo PDF é válido e acessível

        Args:
            file_path (str): Caminho para o arquivo PDF

        Returns:
            Tuple[bool, str]: (é_válido, mensagem_erro)
        """
        if not os.path.exists(file_path):
            return False, "Arquivo não encontrado"

        if not file_path.lower().endswith('.pdf'):
            return False, "Arquivo deve ser um PDF"

        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False, "Arquivo PDF está vazio"

            if file_size > 16 * 1024 * 1024:  # 16MB
                return False, "Arquivo PDF muito grande (máximo 16MB)"

        except Exception as e:
            return False, f"Erro ao verificar arquivo: {str(e)}"

        return True, "Arquivo válido"

    @staticmethod
    def validate_extracted_data(data: Dict) -> Tuple[bool, List[str]]:
        """
        Valida os dados extraídos do PDF

        Args:
            data (Dict): Dados extraídos do PDF

        Returns:
            Tuple[bool, List[str]]: (é_válido, lista_de_avisos)
        """
        warnings = []

        # Verificar se há texto extraído
        if not data.get('texto_completo') or len(data['texto_completo'].strip()) < 100:
            warnings.append("Pouco texto extraído do PDF - pode haver problemas na leitura")

        # Verificar se as partes foram identificadas
        partes = data.get('partes', {})
        if not partes.get('autor'):
            warnings.append("Autor não identificado claramente")
        if not partes.get('reu'):
            warnings.append("Réu não identificado claramente")

        # Verificar se há pedidos
        pedidos = data.get('pedidos', [])
        if not pedidos:
            warnings.append("Nenhum pedido específico identificado")

        # Verificar tipo de ação
        if data.get('tipo_acao') == 'não identificado':
            warnings.append("Tipo de ação não foi identificado automaticamente")

        # Se há muitos avisos, considerar como problemático
        is_valid = len(warnings) < 3

        return is_valid, warnings

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Limpa e sanitiza texto extraído

        Args:
            text (str): Texto a ser sanitizado

        Returns:
            str: Texto limpo
        """
        if not text:
            return ""

        # Remover caracteres especiais problemáticos
        text = text.replace('\x00', '')  # Null bytes
        text = text.replace('\r\n', '\n')  # Normalizar quebras de linha
        text = text.replace('\r', '\n')

        # Remover espaços excessivos
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            cleaned_line = ' '.join(line.split())  # Remove espaços múltiplos
            if cleaned_line:  # Só adiciona linhas não vazias
                cleaned_lines.append(cleaned_line)

        return '\n'.join(cleaned_lines)


def validar_dados_advogado(dados: Dict, campos_obrigatorios: List[str]) -> List[str]:
    """
    Valida os dados do advogado e retorna uma lista de erros (se houver).

    Args:
        dados (Dict): Dados do advogado
        campos_obrigatorios (List[str]): Lista de campos obrigatórios

    Returns:
        List[str]: Lista de mensagens de erro
    """
    erros = []
    for campo in campos_obrigatorios:
        if campo not in dados or not str(dados[campo]).strip():
            erros.append(f"Campo obrigatório '{campo}' está ausente ou vazio.")
    return erros
def validar_dados_advogado(dados: dict, campos_obrigatorios: list) -> list:
    """
    Valida campos obrigatórios do advogado.

    Args:
        dados (dict): Dicionário com os dados do advogado.
        campos_obrigatorios (list): Lista com os nomes dos campos obrigatórios.

    Returns:
        list: Lista com os nomes dos campos ausentes.
    """
    ausentes = []
    for campo in campos_obrigatorios:
        valor = dados.get(campo, "").strip() if isinstance(dados.get(campo), str) else dados.get(campo)
        if not valor:
            ausentes.append(campo)
    return ausentes
