# admin/turma/routes.py
from flask import render_template, request, session, redirect, url_for
from . import turma_bp
from app.models import Aluno, Prof, Turma
from app import db

@turma_bp.route('/novaturma', methods=['POST', 'GET'])
def nova_turma():
    usuario = session.get('usuario', None)
    if not usuario or (usuario != 'admin' and usuario != 'professor'):
        return redirect(url_for('routes.home'))

    if usuario == 'professor':
        profs = Prof.query.filter_by(idProf=session.get('idProf', None)).all()
    else:
        profs = Prof.query.all()

    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        idProf = request.form.get('prof')

        if not nome or not descricao or not idProf:
            mensagem = 'Por favor, preencha todos os campos.'
            return render_template('turma.html', mensagem=mensagem, profs=profs)

        nova_turma = Turma(nome=nome, descricao=descricao, idProf =idProf)
        db.session.add(nova_turma)
        db.session.commit()

        if usuario == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('prof.prof_dashboard'))

    return render_template('turma.html', profs=profs)

@turma_bp.route('/editarturma/<int:id>', methods=['POST', 'GET'])
def editar_turma(id):
    usuario = session.get('usuario', None)
    if not usuario or (usuario != 'admin' and usuario != 'professor'):
        return redirect(url_for('routes.home'))
    
    turma = Turma.query.get(id)

    if usuario == 'professor':
        profs = Prof.query.filter_by(idProf=session.get('idProf', None)).all()
    else:
        profs = Prof.query.all()

    if not turma:
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        idProf = request.form.get('prof')
        
        turma.nome = nome
        turma.descricao = descricao
        turma.idProf = idProf

        db.session.commit()

        if usuario == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('prof.prof_dashboard'))


    return render_template('turma.html', turma=turma, profs=profs, editar_turma=True)

@turma_bp.route('/excluirturma/<int:id>')
def excluir_turma(id):
    usuario = session.get('usuario', None)
    if not usuario or (usuario != 'admin' and usuario != 'professor'):
        return redirect(url_for('routes.home'))

    turma = Turma.query.get(id)

    if not turma:
         return redirect(url_for('admin.admin_dashboard'))

    db.session.delete(turma)
    db.session.commit()

    if usuario == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    else:
        return redirect(url_for('prof.prof_dashboard'))