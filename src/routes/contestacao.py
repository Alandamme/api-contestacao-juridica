@contestacao_bp.route('/gerar-contestacao-ia-avancada', methods=['POST'])
def gerar_contestacao_ia_avancada():
    try:
        data = request.get_json()
        if not data or 'session_file' not in data:
            return jsonify({'error': 'Dados da sessão não fornecidos'}), 400

        session_file = data['session_file']
        if not os.path.exists(session_file):
            return jsonify({'error': 'Sessão expirada ou inválida'}), 400

        with open(session_file, 'r', encoding='utf-8') as f:
            dados_extraidos = json.load(f)

        dados_reu = data.get('dados_reu', {})

        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            return jsonify({'error': 'OPENAI_API_KEY não configurada no ambiente'}), 500

        # Inicializa gerador com IA
        ia_generator = ContestacaoIAGenerator(api_key=OPENAI_API_KEY)

        # Gera argumentos jurídicos com IA
        argumentos_ia = ia_generator.gerar_argumentacao_ia(dados_extraidos.get('fatos', ''))

        # Junta todos os dados da petição + advogado + IA
        dados_completos = {
            **(dados_extraidos.get('autor') or {}),
            **(dados_extraidos.get('reu') or {}),
            'tipo_acao': dados_extraidos.get('tipo_acao', ''),
            'valor_causa': dados_extraidos.get('valor_causa', ''),
            **dados_reu,
            **argumentos_ia
        }

        # Caminho do modelo DOCX com placeholders
        modelo_docx = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'static', 'modelos',
            'modelo_contestacao_com_placeholders.docx'
        )

        if not os.path.exists(modelo_docx):
            return jsonify({'error': 'Modelo Word (.docx) com placeholders não encontrado'}), 500

        # Caminho de saída
        unique_id = str(uuid.uuid4())[:8]
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        word_path = os.path.join(output_dir, f'contestacao_{unique_id}.docx')

        # Geração do documento Word final
        doc_generator = DocumentGenerator()
        doc_generator.create_word_document_from_template(modelo_docx, word_path, dados_completos)

        return jsonify({
            'message': 'Contestação gerada com sucesso no modelo Word (.docx)',
            'contestacao_id': unique_id,
            'files': {
                'word': word_path
            },
            'preview': 'Arquivo Word gerado com sucesso. Faça o download para visualização completa.'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Erro na geração avançada com IA: {str(e)}'}), 500

