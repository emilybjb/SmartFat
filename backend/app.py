from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

from .routes.alunos import alunos_bp
from .routes.planos import planos_bp
from .routes.mensalidades import mensalidades_bp
from .routes.financeiro import financeiro_bp
from .routes.acesso import acesso_bp
from .routes.treinos import treinos_bp
from .routes.relatorios import relatorios_bp
from .routes.auth import auth_bp

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'smartfat_dev_key')
JWTManager(app)

# Registra blueprints
app.register_blueprint(auth_bp,         url_prefix='/api/auth')
app.register_blueprint(alunos_bp,       url_prefix='/api/alunos')
app.register_blueprint(planos_bp,       url_prefix='/api/planos')
app.register_blueprint(mensalidades_bp, url_prefix='/api/mensalidades')
app.register_blueprint(financeiro_bp,   url_prefix='/api/financeiro')
app.register_blueprint(acesso_bp,       url_prefix='/api/acesso')
app.register_blueprint(treinos_bp,      url_prefix='/api/treinos')
app.register_blueprint(relatorios_bp,   url_prefix='/api/relatorios')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
