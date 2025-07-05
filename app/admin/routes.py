# admin/routes.py
from flask import render_template, session, redirect, url_for
from . import admin_bp  # Importa o Blueprint criado no __init__.py
from app.models import Aluno, Prof, Atividade, Turma  # Importa os modelos
from sqlalchemy.orm import joinedload # Para eager loading (melhor performance)

@admin_bp.route('/')
def admin_dashboard():
    usuario = session.get('usuario', None)
    if not usuario or usuario != 'admin':
        return redirect(url_for('routes.home'))

    alunos = Aluno.query.options(joinedload(Aluno.turma)).all()
    profs = Prof.query.all()
    turmas = Turma.query.options(joinedload(Turma.prof)).all()
    atividades = Atividade.query.options(joinedload(Atividade.criador_prof)).all()
 
    return render_template('admin.html', alunos=alunos, profs=profs, atividades=atividades, turmas=turmas, usuario="Admin")
    

