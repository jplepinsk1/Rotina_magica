# aluno/__init__.py
from flask import Blueprint

turma_bp = Blueprint('turma', __name__)

from . import routes  # Importa as rotas para registrar no Blueprint