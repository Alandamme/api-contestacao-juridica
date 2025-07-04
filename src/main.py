import os
import sys
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS

# Ajusta path base para importar os módulos corretamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.user import db
from src.routes.user import user_bp
from src.routes.contestacao import contestacao_bp
from src.routes.testar_ia import testar_ia_bp  # IA jurídica

# Inicializa app Flask
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), 'static'),
    template_folder=os.path.join(os.path.dirname(__file__), 'templates')
)

# Configurações do Flask
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'senha-padrao-para_desenvolvimento')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ativa CORS
CORS(app)

# Inicializa DB
db.init_app(app)
with app.app_context():
    db.create_all()

# Registra as rotas
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(contestacao_bp, url_prefix='/api')
app.register_blueprint(testar_ia_bp)

# Pasta para downloads de .docx
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Página principal
@app.route('/')
def home():
    return render_template('index.html')

# Healthcheck
@app.route('/api/health')
def health():
    return "ok", 200

# Execução local (não interfere no Gunicorn do Render)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

