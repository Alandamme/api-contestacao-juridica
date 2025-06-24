import os
import sys
from flask import Flask, render_template
from flask_cors import CORS

# Corrige o path para importar corretamente os módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from src.routes.user import user_bp
from src.routes.contestacao import contestacao_bp

# Cria a instância da aplicação
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), 'static'),
    template_folder=os.path.join(os.path.dirname(__file__), 'templates')
)

# Configurações básicas
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'senha-padrao-para_desenvolvimento')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ativa CORS
CORS(app)

# Inicializa o banco
db.init_app(app)
with app.app_context():
    db.create_all()

# Registra as rotas (blueprints)
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(contestacao_bp, url_prefix='/api')

# Rota principal: serve o index.html
@app.route('/')
def home():
    return render_template('index.html')

# Healthcheck
@app.route('/api/health')
def health():
    return "ok", 200

# Executa a aplicação
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
