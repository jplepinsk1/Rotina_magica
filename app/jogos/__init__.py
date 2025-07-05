from flask import Blueprint

jogos_bp = Blueprint('jogos', __name__)

from . import routes  # Importa as rotas para registrar no Blueprint