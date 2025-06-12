"""
Gerador de contestações jurídicas baseado em templates
"""

from datetime import datetime
from typing import Dict, List
import os
import re

class ContestacaoGenerator:
    """
    Classe responsável por gerar contestações jurídicas automatizadas
    """
    
    def __init__(self):
        self.template_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 'templates', 'template_contestacao.txt'
        )
        self.argumentos_defesa = self._load_defense_arguments()
    
    def _load_defense_arguments(self) -> Dict:
        """
        Carrega argumentos de defesa padrão por tipo de ação
        """
        return {
            'indenização': {
                'preliminares': [
                    "1.1 - DA AUSÊNCIA DE PRESSUPOSTO PROCESSUAL",
                    "Preliminarmente, cumpre destacar que a petição inicial não demonstra de forma clara e objetiva os fatos constitutivos do direito alegado pelo autor, configurando inépcia da inicial, nos termos do artigo 330, § 1º, inciso II, do Código de Processo Civil."
                ],
                'merito': [
                    "2.1 - DA AUSÊNCIA DE ATO ILÍCITO",
                    "Não há qualquer ato ilícito praticado pela contestante que possa ensejar o dever de indenizar. A conduta da ré pautou-se sempre pela legalidade e boa-fé.",
                    "",
                    "2.2 - DA INEXISTÊNCIA DE DANO MORAL",
                    "Os fatos narrados pelo autor configuram mero aborrecimento cotidiano, insuscetível de gerar dano moral indenizável. Conforme entendimento consolidado dos tribunais superiores, nem todo dissabor configura dano moral.",
                    "",
                    "2.3 - DA AUSÊNCIA DE NEXO CAUSAL",
                    "Ainda que se admita a existência de algum transtorno, este não decorreu de conduta da contestante, inexistindo nexo causal entre qualquer ação da ré e os alegados danos."
                ],
                'fundamentacao': [
                    "Artigo 186 do Código Civil - 'Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito.'",
                    "",
                    "Artigo 927 do Código Civil - 'Aquele que, por ato ilícito (arts. 186 e 187), causar dano a outrem, fica obrigado a repará-lo.'",
                    "",
                    "Súmula 385 do STJ - 'Da anotação irregular em cadastro de proteção ao crédito, não cabe indenização por dano moral, quando preexistente legítima inscrição, ressalvado o direito ao cancelamento.'"
                ],
                'pedidos': [
                    "a) O acolhimento das preliminares arguidas, com a consequente extinção do processo sem resolução do mérito;",
                    "b) Subsidiariamente, a total improcedência dos pedidos formulados na inicial;",
                    "c) A condenação do autor ao pagamento das custas processuais e honorários advocatícios."
                ]
            },
            'cobrança': {
                'preliminares': [
                    "1.1 - DA PRESCRIÇÃO",
                    "O direito de cobrança encontra-se prescrito, nos termos dos artigos 189 e seguintes do Código Civil, tendo decorrido o prazo legal para o exercício da pretensão."
                ],
                'merito': [
                    "2.1 - DO PAGAMENTO JÁ EFETUADO",
                    "O débito objeto da presente ação já foi quitado pelo contestante, conforme documentos que serão oportunamente juntados aos autos.",
                    "",
                    "2.2 - DA INEXIGIBILIDADE DO DÉBITO",
                    "O débito cobrado é inexigível, uma vez que não há relação jurídica válida que o justifique."
                ],
                'fundamentacao': [
                    "Artigo 189 do Código Civil - 'Violado o direito, nasce para o titular a pretensão, a qual se extingue, pela prescrição, nos prazos a que aludem os arts. 205 e 206.'",
                    "",
                    "Artigo 320 do Código Civil - 'A quitação, que sempre poderá ser dada por instrumento particular, designará o valor e a espécie da dívida quitada, o nome do devedor, ou quem por este pagou, o tempo e o lugar do pagamento, com a assinatura do credor, ou do seu representante.'"
                ],
                'pedidos': [
                    "a) O reconhecimento da prescrição, com a consequente extinção do processo com resolução do mérito;",
                    "b) Subsidiariamente, o reconhecimento da quitação do débito;",
                    "c) A condenação do autor ao pagamento das custas processuais e honorários advocatícios."
                ]
            },
            'revisional': {
                'preliminares': [],
                'merito': [
                    "2.1 - DA VALIDADE DAS CLÁUSULAS CONTRATUAIS",
                    "As cláusulas contratuais são válidas e foram livremente pactuadas entre as partes, devendo ser respeitado o princípio do pacta sunt servanda.",
                    "",
                    "2.2 - DA AUSÊNCIA DE ONEROSIDADE EXCESSIVA",
                    "Não há onerosidade excessiva nas cláusulas contratuais, que se encontram em conformidade com as práticas de mercado e a legislação vigente."
                ],
                'fundamentacao': [
                    "Artigo 421 do Código Civil - 'A liberdade contratual será exercida nos limites da função social do contrato.'",
                    "",
                    "Artigo 478 do Código Civil - 'Nos contratos de execução continuada ou diferida, se a prestação de uma das partes se tornar excessivamente onerosa, com extrema vantagem para a outra, em virtude de acontecimentos extraordinários e imprevisíveis, poderá o devedor pedir a resolução do contrato.'"
                ],
                'pedidos': [
                    "a) A total improcedência dos pedidos formulados na inicial;",
                    "b) A manutenção integral das cláusulas contratuais;",
                    "c) A condenação do autor ao pagamento das custas processuais e honorários advocatícios."
                ]
            }
        }
    
    def generate_contestacao(self, dados_extraidos: Dict, dados_reu: Dict = None) -> str:
        """
        Gera uma contestação baseada nos dados extraídos da petição inicial
        
        Args:
            dados_extraidos (Dict): Dados extraídos da petição inicial
            dados_reu (Dict): Dados do réu para personalização
            
        Returns:
            str: Contestação gerada
        """
        # Carregar template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Preparar dados para substituição
        tipo_acao = dados_extraidos.get('tipo_acao', 'não identificado')
        
        # Obter argumentos específicos para o tipo de ação
        argumentos = self.argumentos_defesa.get(tipo_acao, self.argumentos_defesa['indenização'])
        
        # Dados padrão do réu (podem ser personalizados)
        if not dados_reu:
            dados_reu = {
                'qualificacao_reu': 'pessoa jurídica de direito privado, devidamente inscrita no CNPJ',
                'advogado_reu': 'Advogado da Contestante',
                'oab_numero': '000.000',
                'estado': 'SP'
            }
        
        # Preparar substituições
        substituicoes = {
            'vara': 'VARA CÍVEL',
            'comarca': 'SÃO PAULO/SP',
            'reu': dados_extraidos.get('partes', {}).get('reu', 'CONTESTANTE'),
            'qualificacao_reu': dados_reu.get('qualificacao_reu'),
            'tipo_acao': tipo_acao.upper(),
            'autor': dados_extraidos.get('partes', {}).get('autor', 'AUTOR'),
            'preliminares': self._format_section(argumentos['preliminares']),
            'merito': self._format_section(argumentos['merito']),
            'contestacao_fatos': self._generate_facts_response(dados_extraidos),
            'fundamentacao_juridica': self._format_section(argumentos['fundamentacao']),
            'pedidos_contestacao': self._format_section(argumentos['pedidos']),
            'cidade': 'São Paulo',
            'data': datetime.now().strftime('%d de %B de %Y'),
            'advogado_reu': dados_reu.get('advogado_reu'),
            'estado': dados_reu.get('estado'),
            'oab_numero': dados_reu.get('oab_numero')
        }
        
        # Aplicar substituições
        contestacao = template
        for key, value in substituicoes.items():
            contestacao = contestacao.replace(f'{{{key}}}', str(value))
        
        return contestacao
    
    def _format_section(self, items: List[str]) -> str:
        """
        Formata uma seção da contestação
        """
        if not items:
            return "Não aplicável ao caso em tela."
        
        return '\n\n'.join(items)
    
    def _generate_facts_response(self, dados_extraidos: Dict) -> str:
        """
        Gera resposta aos fatos alegados pelo autor
        """
        fatos_autor = dados_extraidos.get('fatos', '')
        
        if not fatos_autor:
            return "A contestante impugna genericamente os fatos alegados pelo autor, por não corresponderem à verdade."
        
        response = [
            "A contestante vem impugnar os fatos alegados pelo autor, esclarecendo que:",
            "",
            "Os fatos narrados na inicial não condizem com a realidade. A contestante sempre pautou sua conduta pela legalidade e boa-fé, não havendo qualquer irregularidade em seus procedimentos.",
            "",
            "Ademais, os alegados transtornos configuram mero aborrecimento cotidiano, inerente à vida em sociedade, não ensejando qualquer tipo de indenização."
        ]
        
        return '\n'.join(response)
    
    def save_contestacao_to_file(self, contestacao: str, filename: str) -> str:
        """
        Salva a contestação em arquivo
        
        Args:
            contestacao (str): Texto da contestação
            filename (str): Nome do arquivo
            
        Returns:
            str: Caminho do arquivo salvo
        """
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(contestacao)
        
        return file_path

