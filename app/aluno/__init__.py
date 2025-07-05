# aluno/__init__.py
from flask import Blueprint

aluno_bp = Blueprint('aluno', __name__)

from . import routes  # Importa as rotas para registrar no Blueprint