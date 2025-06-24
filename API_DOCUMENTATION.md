# Documentação da API de Geração de Contestação Jurídica

## Visão Geral

Esta API permite o upload de petições iniciais em formato PDF, análise automática do conteúdo jurídico e geração de contestações personalizadas com base em templates pré-definidos.

## URL Base

```
https://5001-izfrwdt80n67xqenc575h-8ee2ca4c.manusvm.computer
```

## Endpoints

### 1. Health Check

**GET** `/api/health`

Verifica se a API está funcionando corretamente.

**Resposta:**
```json
{
  "status": "API funcionando corretamente",
  "version": "1.0.0",
  "endpoints": [
    "/api/upload - POST - Upload de petição inicial em PDF",
    "/api/generate-contestacao - POST - Geração de contestação",
    "/api/download/<type>/<id> - GET - Download de documentos",
    "/api/health - GET - Status da API"
  ]
}
```

### 2. Upload de Petição Inicial

**POST** `/api/upload`

Faz upload de um arquivo PDF contendo a petição inicial e processa automaticamente o conteúdo.

**Parâmetros:**
- `file` (multipart/form-data): Arquivo PDF da petição inicial

**Resposta de Sucesso:**
```json
{
  "message": "Arquivo processado com sucesso",
  "filename": "peticao_inicial.pdf",
  "file_path": "/tmp/tmpXXXXXX/peticao_inicial.pdf",
  "session_file": "/tmp/tmpXXXXXX/dados_extraidos.json",
  "dados_extraidos": {
    "partes": {
      "autor": "João da Silva",
      "reu": "Empresa XYZ LTDA"
    },
    "tipo_acao": "indenização",
    "valor_causa": "11.500,00",
    "pedidos_count": 3,
    "fundamentos_juridicos": ["CDC", "Código Civil"]
  },
  "data_valid": true,
  "warnings": []
}
```

**Resposta de Erro:**
```json
{
  "error": "Tipo de arquivo não permitido. Apenas PDFs são aceitos."
}
```

### 3. Geração de Contestação

**POST** `/api/generate-contestacao`

Gera uma contestação jurídica baseada nos dados extraídos da petição inicial.

**Parâmetros (JSON):**
```json
{
  "session_file": "/tmp/tmpXXXXXX/dados_extraidos.json",
  "dados_reu": {
    "advogado_reu": "Dr. João Silva",
    "oab_numero": "123.456",
    "estado": "SP"
  }
}
```

**Resposta de Sucesso:**
```json
{
  "message": "Contestação gerada com sucesso",
  "contestacao_id": "abc12345",
  "files": {
    "txt": "/path/to/contestacao_abc12345.txt",
    "word": "/path/to/contestacao_abc12345.docx",
    "pdf": "/path/to/contestacao_abc12345.pdf"
  },
  "preview": "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO..."
}
```

### 4. Download de Documentos

**GET** `/api/download/<file_type>/<contestacao_id>`

Faz download dos documentos gerados.

**Parâmetros:**
- `file_type`: Tipo do arquivo (`txt`, `word`, `pdf`)
- `contestacao_id`: ID da contestação gerada

**Exemplo:**
```
GET /api/download/pdf/abc12345
```

## Exemplos de Uso

### Exemplo com cURL

1. **Upload de PDF:**
```bash
curl -X POST \
  https://5001-izfrwdt80n67xqenc575h-8ee2ca4c.manusvm.computer/api/upload \
  -F "file=@peticao_inicial.pdf"
```

2. **Geração de Contestação:**
```bash
curl -X POST \
  https://5001-izfrwdt80n67xqenc575h-8ee2ca4c.manusvm.computer/api/generate-contestacao \
  -H "Content-Type: application/json" \
  -d '{
    "session_file": "/tmp/tmpXXXXXX/dados_extraidos.json",
    "dados_reu": {
      "advogado_reu": "Dr. João Silva",
      "oab_numero": "123.456",
      "estado": "SP"
    }
  }'
```

3. **Download de PDF:**
```bash
curl -X GET \
  https://5001-izfrwdt80n67xqenc575h-8ee2ca4c.manusvm.computer/api/download/pdf/abc12345 \
  -o contestacao.pdf
```

### Exemplo com Python

```python
import requests

# 1. Upload do PDF
with open('peticao_inicial.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'https://5001-izfrwdt80n67xqenc575h-8ee2ca4c.manusvm.computer/api/upload',
        files=files
    )
    upload_result = response.json()

# 2. Gerar contestação
session_file = upload_result['session_file']
dados_reu = {
    'advogado_reu': 'Dr. João Silva',
    'oab_numero': '123.456',
    'estado': 'SP'
}

response = requests.post(
    'https://5001-izfrwdt80n67xqenc575h-8ee2ca4c.manusvm.computer/api/generate-contestacao',
    json={
        'session_file': session_file,
        'dados_reu': dados_reu
    }
)
contestacao_result = response.json()

# 3. Download do PDF
contestacao_id = contestacao_result['contestacao_id']
response = requests.get(
    f'https://5001-izfrwdt80n67xqenc575h-8ee2ca4c.manusvm.computer/api/download/pdf/{contestacao_id}'
)

with open('contestacao_gerada.pdf', 'wb') as f:
    f.write(response.content)
```

## Interface Web

A API inclui uma interface web interativa disponível em:
```
https://5001-izfrwdt80n67xqenc575h-8ee2ca4c.manusvm.computer
```

A interface permite:
- Upload de arquivos PDF via drag-and-drop ou seleção
- Visualização dos dados extraídos da petição
- Personalização dos dados do réu
- Geração e download da contestação em múltiplos formatos

## Tipos de Ação Suportados

A API reconhece automaticamente os seguintes tipos de ação:

1. **Indenização** - Ações de danos morais e materiais
2. **Cobrança** - Ações de cobrança de débitos
3. **Revisional** - Ações de revisão contratual
4. **Consignação** - Ações de consignação em pagamento
5. **Rescisão** - Ações de rescisão contratual

## Argumentos de Defesa

Para cada tipo de ação, a API utiliza argumentos de defesa específicos:

### Indenização
- Ausência de ato ilícito
- Inexistência de dano moral
- Ausência de nexo causal
- Mero aborrecimento cotidiano

### Cobrança
- Prescrição da dívida
- Pagamento já efetuado
- Inexigibilidade do débito

### Revisional
- Validade das cláusulas contratuais
- Ausência de onerosidade excessiva
- Princípio do pacta sunt servanda

## Limitações

- Tamanho máximo do arquivo: 16MB
- Formatos aceitos: PDF apenas
- Sessões temporárias (dados são limpos periodicamente)
- API em modo de desenvolvimento (não usar em produção)

## Códigos de Status HTTP

- `200` - Sucesso
- `400` - Erro na requisição (arquivo inválido, parâmetros faltando)
- `404` - Arquivo não encontrado
- `500` - Erro interno do servidor

## Suporte

Esta é uma API de demonstração criada para fins educacionais. Para uso em produção, é necessário:

1. Implementar autenticação e autorização
2. Usar servidor WSGI em produção (Gunicorn, uWSGI)
3. Implementar persistência de dados adequada
4. Adicionar logs e monitoramento
5. Revisar e validar todas as contestações geradas por um advogado qualificado

