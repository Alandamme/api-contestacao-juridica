from docxtpl import DocxTemplate
from datetime import datetime
import os

MODELO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "modelos", "modelo_contestacao_com_placeholders_pronto.docx"))
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# dentro de testar_ia()
...
corpo_gerado = ""
for chunk in stream:
    if chunk.choices[0].delta.content:
        corpo_gerado += chunk.choices[0].delta.content

# gera o Word com o conteúdo
doc = DocxTemplate(MODELO_PATH)
context = { "corpo_contestacao": corpo_gerado.strip() }
doc.render(context)

timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
output_filename = f"preview_ia_{timestamp}.docx"
output_path = os.path.join(UPLOAD_FOLDER, output_filename)
doc.save(output_path)

# resposta com link
return jsonify({
    "mensagem": "Pré-visualização gerada com sucesso!",
    "corpo_gerado": corpo_gerado.strip(),
    "arquivo_word": f"/download/{output_filename}"
}), 200

