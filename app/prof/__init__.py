# prof/__init__.py
from flask import Blueprint

prof_bp = Blueprint('prof', __name__)

from . import routes  # Importa as rotas para registrar no Blueprint