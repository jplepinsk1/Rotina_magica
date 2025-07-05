# admin/__init__.py
from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from . import routes  # Importa as rotas para registrar no Blueprint