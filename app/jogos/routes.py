from flask import render_template, request, session, redirect, url_for
from . import jogos_bp
from app.models import Atividade, AtvQuebracabeca, AlunoAtividade
from app import db
from sqlalchemy.orm import joinedload

@jogos_bp.route('/jogo/<int:idTurmaAtividade>/<int:idAtividade>')
def jogos(idTurmaAtividade, idAtividade):
    usuario = session.get('usuario', None)
    if not usuario or usuario != 'aluno':
        return redirect(url_for('routes.home'))
    if not idAtividade:
        return redirect(url_for('aluno.aluno_page'))

    session['idTurmaAtividade'] = idTurmaAtividade

    atividade = Atividade.query.get(idAtividade)
    if atividade.tipo == "Quebra-cabeça":
        dados_quebra_cabeca = AtvQuebracabeca.query.filter_by(idAtividade=idAtividade).first()
        return render_template('quebracabeca/index.html', atividade=atividade, imagem_quebracabeca= dados_quebra_cabeca.imagem_url)


@jogos_bp.route('/vitoria')
def vitoria():
    usuario = session.get('usuario', None)
    if not usuario or usuario != 'aluno':
        return redirect(url_for('routes.home'))
    idAluno = session.get('idAluno', None)


    idTurmaAtividade = session.get('idTurmaAtividade')
    tempo = request.args.get('tempo', type=int)
    pontuacao = request.args.get('pontuacao', type=int)
    print(f'{idTurmaAtividade} {tempo}  {pontuacao}' )
    if idTurmaAtividade and tempo is not None and pontuacao is not None:
        
        # Adicionar tentativa
        tentativas_anteriores = AlunoAtividade.query.filter_by(
            idAluno=idAluno,
            idTurmaAtividade=idTurmaAtividade
        ).count()

        nova_tentativa = tentativas_anteriores + 1

        registro = AlunoAtividade(
        idAluno=idAluno,
        idTurmaAtividade=idTurmaAtividade,
        tempo_segundos=tempo,
        pontuacao=pontuacao,
        tentativa=nova_tentativa
        )

        # Adiciona e confirma no banco de dados
        db.session.add(registro)
        db.session.commit()
        session.pop('idTurmaAtividade', None)

    return redirect(url_for('aluno.aluno_page'))
    

    