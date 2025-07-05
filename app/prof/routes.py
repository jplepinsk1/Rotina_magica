# admin/professores/routes.py
from flask import render_template, request, session, redirect, url_for, flash
from . import prof_bp  # Importa o Blueprint
from app.models import Prof, Aluno, Atividade, Turma, TurmaAtividade
from app import db
from sqlalchemy.orm import joinedload

@prof_bp.route('/novoprof', methods=['POST', 'GET'])
def novo_prof():
    usuario = session.get('usuario', None)
    if not usuario or session.get('usuario') != 'admin':
        return redirect(url_for('routes.home'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        login = request.form.get('login')
        senha = request.form.get('senha')

        if not nome or not login or not senha:
            mensagem = 'Por favor, preencha todos os campos.'
            return render_template('prof.html', mensagem=mensagem)
        
        professor_existente = Prof.query.filter_by(login=login).first()
        aluno_existente = Aluno.query.filter_by(login=login).first()

        if professor_existente or aluno_existente or login == 'admin':
            mensagem = "Login inválido! Escolha outro!"
            return render_template("prof.html", erro_login=mensagem, nome=nome, login=login, senha=senha)

        novo_prof = Prof(nome=nome, login=login, senha=senha, status=1)
        db.session.add(novo_prof)
        db.session.commit()

        return redirect(url_for('admin.admin_dashboard'))

    return render_template('prof.html')

@prof_bp.route('/editarprof/<int:id>', methods=['POST', 'GET'])
def editar_prof(id):
    usuario = session.get('usuario', None)
    if not usuario or session.get('usuario') != 'admin':
        return redirect(url_for('routes.home'))

    prof = Prof.query.get(id)

    if not prof:
        return redirect(url_for('admin.admin_dashboard'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        novo_login = request.form.get('login')
        senha = request.form.get('senha')
        status = request.form.get('status')

        

        if prof.login != novo_login:
            professor_existente = Prof.query.filter_by(login=novo_login).first()
            aluno_existente = Aluno.query.filter_by(login=novo_login).first()

            if professor_existente or aluno_existente or novo_login == 'admin':
                mensagem = "Login inválido! Escolha outro!"
                return render_template("prof.html", erro_login=mensagem, nome=nome, login=novo_login, senha=senha, prof=prof, editar_prof=True)

        prof.nome = nome
        prof.login = novo_login
        prof.senha = senha
        prof.status = status


        db.session.commit()

        return redirect(url_for('admin.admin_dashboard'))

    return render_template('prof.html', prof=prof, editar_prof=True)

@prof_bp.route('/excluirprof/<int:id>')
def excluir_prof(id):
    usuario = session.get('usuario', None)
    if not usuario or session.get('usuario') != 'admin':
        return redirect(url_for('routes.home'))

    prof = Prof.query.get(id)

    if not prof:
        return redirect(url_for('admin.admin_dashboard'))

    turmas = Turma.query.filter_by(idProf=id).all()

    if turmas:
        flash(f"Não é possível excluir o professor {prof.nome}, pois há turmas vinculadas a ele(a)!", "erro")
        return redirect(url_for('admin.admin_dashboard'))


    db.session.delete(prof)
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@prof_bp.route('/dashboard')
def prof_dashboard():
    usuario = session.get('usuario', None)
    if not usuario or usuario != 'professor':
        return redirect(url_for('routes.home'))
    
    idProf = session.get('idProf', None)
    if not idProf:
        return redirect(url_for('routes.home'))
    
    professor = Prof.query.get(idProf)

    # Turmas do professor
    turmas = Turma.query.filter_by(idProf=idProf).all()
    ids_turmas = [turma.idTurma for turma in turmas]

    # Alunos somente das turmas desse professor
    alunos = Aluno.query.filter(Aluno.idTurma.in_(ids_turmas)).all()

    # Atividades criadas pelo professor
    atividades = Atividade.query.filter_by(idProf=idProf).all()

    # Atividades atribuídas somente para as turmas do professor
    turma_atividades = (
    TurmaAtividade.query
    .filter(TurmaAtividade.idTurma.in_(ids_turmas))
    .options(
        joinedload(TurmaAtividade.atividade).joinedload(Atividade.criador_prof),
        joinedload(TurmaAtividade.turma)
    )
    .all()
    )


    return render_template(
        'prof_dashboard.html',
        professor=professor,
        turmas=turmas,
        alunos=alunos,
        atividades=atividades,
        turma_atividades=turma_atividades,
        usuario=professor.nome
    )

