from flask import Blueprint, render_template, request, redirect, url_for, session
import os
from dotenv import load_dotenv
from .models import Aluno, Prof
from . import db

load_dotenv()

bp_routes = Blueprint('routes', __name__)

@bp_routes.route('/')
def home():
    usuario = session.get('usuario', None)
    if usuario:
        if usuario == 'aluno':
            return redirect(url_for('aluno.aluno_page'))
        

    return render_template('home.html')


@bp_routes.route('/login', methods=['GET','POST'])
def login():
    if request.method != 'POST':
        return redirect('/')

    usuario = request.form.get('usuario', None)
    senha = request.form.get('senha', None)

    if not usuario or not senha:
        mensagem = 'Por favor, preencha todos os campos.'
        return render_template('home.html', mensagem=mensagem)

    if usuario == 'admin' and senha == os.getenv('ADM_PASSWORD'):
        session['usuario'] = 'admin'
        return redirect(url_for('admin.admin_dashboard'))  

    professor = db.session.query(Prof.idProf).filter_by(login=usuario, senha=senha).first()

    if professor:
        session['usuario'] = "professor"
        session['idProf'] = professor.idProf
        return redirect(url_for('prof.prof_dashboard')) 

    aluno = Aluno.query.filter_by(login=usuario, senha=senha).first()
    if aluno:
        session['usuario'] = "aluno"
        session['idAluno'] = aluno.idAluno
        return redirect(url_for('aluno.aluno_page')) 

    
    mensagem = "Usuário ou senha incorretos."
    return render_template('home.html', mensagem=mensagem)


@bp_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('routes.home')) 

@bp_routes.route('/projeto')
def projeto():
    return render_template('projeto.html')

@bp_routes.route('/familias')
def familias():
    return render_template('familias.html')
    
@bp_routes.route('/educadores')
def educadores():
    return render_template('educadores.html')

@bp_routes.route('/fale')
def fale():
    return render_template('fale.html')






