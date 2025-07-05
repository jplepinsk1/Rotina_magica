# admin/alunos/routes.py
from flask import render_template, request, session, redirect, url_for
from . import aluno_bp
from app.models import Aluno, Prof, Turma, TurmaAtividade, AlunoAtividade
from app import db
from sqlalchemy.orm import joinedload
from sqlalchemy import desc

@aluno_bp.route('/novoaluno', methods=['POST', 'GET'])
def novo_aluno():
    usuario = session.get('usuario', None)
    if not usuario or (usuario != 'admin' and usuario != 'professor'):
        return redirect(url_for('routes.home'))

    if usuario == 'professor':
        turmas = Turma.query.filter_by(idProf=session.get('idProf', None)).all()
    if usuario == 'admin':
        turmas = Turma.query.all()
    
    

    if request.method == 'POST':
        nome = request.form.get('nome')
        login = request.form.get('login')
        dtnasc = request.form.get('dtnasc')
        senha = request.form.get('senha')
        idTurma = request.form.get('turma')

        if not nome or not login or not senha or not idTurma or not dtnasc:
            mensagem = 'Por favor, preencha todos os campos.'
            return render_template('aluno.html', mensagem=mensagem, turmas=turmas)
        
        aluno_existente = Aluno.query.filter_by(login=login).first()
        prof_existente = Prof.query.filter_by(login=login).first()


        if aluno_existente or prof_existente or login == 'admin':
            mensagem = "Login inválido! Escolha outro."
            return render_template("aluno.html", erro_login=mensagem, nome=nome, dtnasc=dtnasc, login=login, senha=senha, turmas=turmas, idTurma=int(idTurma))

        novo_aluno = Aluno(nome=nome, login=login, senha=senha, dataNascimento=dtnasc, idTurma=idTurma)
        db.session.add(novo_aluno)
        db.session.commit()

        if usuario == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('prof.prof_dashboard'))

    return render_template('aluno.html', turmas=turmas)

@aluno_bp.route('/editaraluno/<int:id>', methods=['POST', 'GET'])
def editar_aluno(id):
    usuario = session.get('usuario', None)
    if not usuario or (usuario != 'admin' and usuario != 'professor'):
        return redirect(url_for('routes.home'))
    
    aluno = Aluno.query.get(id)

    if usuario == 'professor':
        turmas = Turma.query.filter_by(idProf=session.get('idProf', None)).all()
    if usuario == 'admin':
        turmas = Turma.query.all()



    if not aluno:
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        novo_login = request.form.get('login')
        dtnasc = request.form.get('dtnasc')
        senha = request.form.get('senha')
        idTurma = request.form.get('turma')
        status = request.form.get('status')

        if aluno.login != novo_login:
            aluno_existente = Aluno.query.filter_by(login=novo_login).first()
            prof_existente = Prof.query.filter_by(login=novo_login).first()
            if aluno_existente or prof_existente or novo_login == 'admin':
                mensagem = "Login inválido! Escolha outro!"
                return render_template("aluno.html",aluno=aluno, erro_login=mensagem, nome=nome, login=novo_login, senha=senha, turmas=turmas, editar_aluno=True)
        
        aluno.nome = nome
        aluno.login = novo_login
        aluno.senha = senha
        aluno.dataNascimento = dtnasc
        aluno.idTurma = idTurma
        aluno.status = status

        db.session.commit()

        if usuario == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('prof.prof_dashboard'))


    return render_template('aluno.html', aluno=aluno, turmas=turmas, editar_aluno=True)

@aluno_bp.route('/excluiraluno/<int:id>')
def excluir_aluno(id):
    usuario = session.get('usuario', None)
    if not usuario or (usuario != 'admin' and usuario != 'professor'):
        return redirect(url_for('routes.home'))

    aluno = Aluno.query.get(id)

    if not aluno:
         return redirect(url_for('admin.admin_dashboard'))

    db.session.delete(aluno)
    db.session.commit()

    if usuario == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    else:
        return redirect(url_for('prof.prof_dashboard'))

@aluno_bp.route('/')
def aluno_page():
    usuario = session.get('usuario', None)
    if not usuario or usuario != 'aluno':
        return redirect(url_for('routes.home'))

    idAluno = session.get('idAluno', None)
    if not idAluno:
        return redirect(url_for('routes.home'))

    aluno = Aluno.query.get(idAluno)

    # Atividades atribuídas à turma do aluno
    atividades_atribuidas = (
        TurmaAtividade.query
        .filter_by(idTurma=aluno.idTurma)
        .options(joinedload(TurmaAtividade.atividade))
        .order_by(TurmaAtividade.dataAtribuicao.desc())
        .all()
    )

    atividades_com_status = []

    for atribuicao in atividades_atribuidas:
        # Busca a última tentativa do aluno para essa atividade atribuída
        ultima_entrada = (
            AlunoAtividade.query
            .filter_by(idAluno=idAluno, idTurmaAtividade=atribuicao.idTurmaAtividade)
            .order_by(AlunoAtividade.data_jogada.desc())
            .first()
        )

        atividades_com_status.append({
            'atribuicao': atribuicao,
            'ultima_pontuacao': ultima_entrada.pontuacao if ultima_entrada else None,
            'ultimo_tempo': ultima_entrada.tempo_segundos if ultima_entrada else None
        })

    return render_template(
        'aluno_dashboard.html',
        aluno=aluno,
        atividades_com_status=atividades_com_status
    )

@aluno_bp.route('/resultados/<int:idAluno>')
def resultados(idAluno):
    usuario = session.get('usuario', None)
    if not usuario or (usuario != 'admin' and usuario != 'professor'):
        return redirect(url_for('routes.home'))

    aluno = Aluno.query.get_or_404(idAluno)

    # Carrega os resultados com os relacionamentos prontos
    resultados = (
        AlunoAtividade.query
        .filter_by(idAluno=idAluno)
        .options(
            joinedload(AlunoAtividade.turma_atividade)
            .joinedload(TurmaAtividade.atividade)
        )
        .order_by(AlunoAtividade.data_jogada.desc())
        .all()
    )

    return render_template(
        'resultados_aluno.html',
        aluno=aluno,
        resultados=resultados
    )
    
