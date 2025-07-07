import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv


load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates')

    # Configurações
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_DATABASE')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 280  # segundos (menos que 300s = 5min)
    app.config['SQLALCHEMY_POOL_PRE_PING'] = True  # testa se a conexão ainda está viva

    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads') # Caminho absoluto

    # Inicializa extensões
    db.init_app(app)

# Teste de conexão com o banco
    with app.app_context():
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print('✅ Conexão com o banco de dados estabelecida com sucesso!')
        except Exception as e:
            print(f'❌ Erro ao conectar no banco de dados: {e}')

    # Importa e registra os Blueprints
    from .admin import admin_bp  # Importação relativa
    from .prof import prof_bp  # Importação relativa
    from .aluno import aluno_bp  # Importação relativa
    from .atividade import atividade_bp  # Importação relativa
    from .turma import turma_bp  # Importação relativa
    from .jogos import jogos_bp  # Importação relativa
    from . import routes  # Importa o Blueprint routes
  
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(prof_bp, url_prefix='/prof')
    app.register_blueprint(aluno_bp, url_prefix='/aluno')
    app.register_blueprint(atividade_bp, url_prefix='/atividade')
    app.register_blueprint(turma_bp, url_prefix='/turma')
    app.register_blueprint(jogos_bp, url_prefix='/jogos')
    app.register_blueprint(routes.bp_routes)  # Registra o Blueprint routes

    # Libera a sessão do banco ao final de cada request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app