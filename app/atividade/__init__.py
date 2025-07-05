# atividade/__init__.py
from flask import Blueprint

atividade_bp = Blueprint('atividade', __name__)

from . import routes  # Importa as rotas para registrar no Blueprint