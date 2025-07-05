from flask import render_template, request, session, redirect, url_for, current_app
from . import atividade_bp
from app.models import Prof, Turma, Atividade, AtvQuebracabeca, TurmaAtividade
from app import db
import os
import uuid
from PIL import Image


@atividade_bp.route('/novaatividade', methods=['POST', 'GET'])
def nova_atividade():
    usuario = session.get('usuario', None)
    if not usuario or (usuario != 'admin' and usuario != 'professor'):
        return redirect(url_for('routes.home'))

    if usuario == 'professor':
        profs = Prof.query.filter_by(idProf=session.get('idProf', None)).all()
    else:
        profs = Prof.query.all()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        nivel = request.form['nivel']
        prof_id = request.form['prof']
        tipo_atividade = request.form['tipoAtividade'] # Changed from 'tipoAtividade' to 'tipo' based on HTML

        if not titulo or not descricao or not nivel or not prof_id or not tipo_atividade:
            mensagem = 'Por favor, preencha todos os campos.'
            return render_template('atividade.html', mensagem=mensagem, profs=profs,
                                   nome=titulo, descricao=descricao, nivel_selecionado=nivel,
                                   idProf_selecionado=prof_id, tipo_selecionado=tipo_atividade) # Keep form data on error

        # Acessando UPLOAD_FOLDER da instância 'app' importada
        upload_folder = current_app.config['UPLOAD_FOLDER']
        image_url = None # Initialize image_url to None

        if tipo_atividade == '1':  # "Quebra-cabeça"
            tipo = "Quebra-cabeça"
            if 'imagem_quebra_cabeca' in request.files:
                file = request.files['imagem_quebra_cabeca']
                if file and file.filename != '':
                    # Garante que a pasta de upload existe
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)

                    # Extrai a extensão e força minúscula
                    extensao = os.path.splitext(file.filename)[1].lower()
                    nome_unico = str(uuid.uuid4()) + extensao
                    caminho_completo_para_salvar = os.path.join(upload_folder, nome_unico)

                    try:
                        # Abre a imagem diretamente do arquivo enviado
                        imagem = Image.open(file.stream)

                        # Redimensiona para no máximo 600x600, mantendo proporção
                        imagem.thumbnail((600, 600))

                        # Salva otimizando conforme tipo
                        if extensao in ['.jpg', '.jpeg']:
                            imagem = imagem.convert("RGB")  # compatível com JPEG
                            imagem.save(caminho_completo_para_salvar, format='JPEG', optimize=True, quality=70)
                        elif extensao == '.png':
                            imagem.save(caminho_completo_para_salvar, format='PNG', optimize=True)
                        else:
                            # Se for outro formato, salva sem compressão
                            file.save(caminho_completo_para_salvar)

                        # Nome final da imagem salva
                        nome_arquivo_salvo = nome_unico

                    except Exception as e:
                        print(f"Erro ao processar a imagem: {e}")
                        mensagem = 'Erro ao processar a imagem. Tente outro arquivo.'
                        return render_template(
                            'atividade.html',
                            mensagem=mensagem,
                            profs=profs,
                            nome=titulo,
                            descricao=descricao,
                            nivel_selecionado=nivel,
                            idProf_selecionado=prof_id,
                            tipo_selecionado=tipo_atividade
                        )
        else:
            mensagem = 'Por favor, selecione uma imagem para o quebra-cabeça.'
            return render_template(
                'atividade.html',
                mensagem=mensagem,
                profs=profs,
                nome=titulo,
                descricao=descricao,
                nivel_selecionado=nivel,
                idProf_selecionado=prof_id,
                tipo_selecionado=tipo_atividade
            )



        # Create a new Atividade object
        nova_atividade_obj = Atividade(
            titulo=titulo,
            descricao=descricao,
            nivel=nivel,
            tipo=tipo,
            idProf=prof_id
        )

        db.session.add(nova_atividade_obj)
        db.session.flush() # Use flush() to get the idAtividade before committing

        # If it's a "Quebra-cabeça", create and link the AtvQuebracabeca
        if tipo_atividade == '1':
            if nome_arquivo_salvo: 
                nova_quebracabeca_detalhe = AtvQuebracabeca(
                    imagem_url=nome_arquivo_salvo,
                    idAtividade=nova_atividade_obj.idAtividade # Link to the newly created activity
                )
                db.session.add(nova_quebracabeca_detalhe)
            else:
                 # This case should ideally be caught by the file validation above,
                 # but as a fallback, handle the missing image for quebra-cabeca
                db.session.rollback() # Rollback the Atividade creation
                mensagem = 'Erro: Imagem do quebra-cabeça não foi enviada.'
                return render_template('atividade.html', mensagem=mensagem, profs=profs,
                                       nome=titulo, descricao=descricao, nivel_selecionado=nivel,
                                       idProf_selecionado=prof_id, tipo_selecionado=tipo_atividade)

        # For other activity types, you would create their respective detail objects here
        # elif tipo_atividade == '2': # Ligue os pontos
        #     nova_liguepontos_detalhe = AtvLiguepontos(...)
        #     db.session.add(nova_liguepontos_detalhe)
        # elif tipo_atividade == '3': # Sequência certa
        #     nova_sequencia_detalhe = AtvSequencia(...)
        #     db.session.add(nova_sequencia_detalhe)

        db.session.commit() # Commit all changes to the database

        if usuario == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('prof.prof_dashboard'))

    # For GET requests or if POST validation fails before commit
    return render_template('atividade.html', profs=profs)


@atividade_bp.route('/editaratividade/<int:id>', methods=['GET', 'POST'])
def editar_atividade(id):
    usuario = session.get('usuario', None)
    if not usuario or (usuario != 'admin' and usuario != 'professor'):
        return redirect(url_for('routes.home'))

    atividade = Atividade.query.get(id)
    if not atividade:
        return redirect(url_for('admin.admin_dashboard' if usuario == 'admin' else 'prof.prof_dashboard'))

    if usuario == 'professor' and atividade.idProf != session.get('idProf'):
        return redirect(url_for('routes.home'))

    profs = Prof.query.filter_by(idProf=session.get('idProf')) if usuario == 'professor' else Prof.query.all()

    if request.method == 'POST':
        atividade.titulo = request.form['titulo']
        atividade.descricao = request.form['descricao']
        atividade.nivel = request.form['nivel']
        atividade.idProf = request.form['prof']
        tipo_atividade = request.form['tipoAtividade'] 
       # Verifica se foi enviada nova imagem
        nova_imagem = request.files.get('imagem_quebra_cabeca')
        
        if nova_imagem and nova_imagem.filename:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            extensao = os.path.splitext(nova_imagem.filename)[1].lower()
            nome_unico = str(uuid.uuid4()) + extensao
            caminho_salvar = os.path.join(upload_folder, nome_unico)
            try:
                # Abre a imagem com Pillow para processar
                imagem = Image.open(nova_imagem.stream)
                imagem.thumbnail((600, 600))  # Reduz o tamanho, mantendo proporção

                if extensao in ['.jpg', '.jpeg']:
                    imagem = imagem.convert("RGB")  # JPEG exige modo RGB
                    imagem.save(caminho_salvar, format='JPEG', optimize=True, quality=70)
                elif extensao == '.png':
                    imagem.save(caminho_salvar, format='PNG', optimize=True)
                else:
                    # Formato não suportado: salva sem compressão
                    nova_imagem.save(caminho_salvar)

            except Exception as e:
                print(f"Erro ao processar a nova imagem: {e}")
                return redirect(request.url)

            # Atualiza ou cria detalhe da imagem
            detalhe = atividade.quebracabeca_detalhe  # já está relacionado

            if detalhe:
                # Remove imagem antiga (opcional)
                caminho_antigo = os.path.join(current_app.root_path, 'static', 'uploads', detalhe.imagem_url)
                if os.path.exists(caminho_antigo):
                    os.remove(caminho_antigo)

                detalhe.imagem_url = nome_unico
            else:
                novo_detalhe = AtvQuebracabeca(imagem_url=nome_unico, atividade_base=atividade)
                db.session.add(novo_detalhe)

        # ✅ importante: garantir que a alteração será persistida
        db.session.commit()
        return redirect(url_for('admin.admin_dashboard' if usuario == 'admin' else 'prof.prof_dashboard'))

    # Resgata tipo de atividade existente
    tipo_atividade = '1' if atividade.quebracabeca_detalhe else '2' if hasattr(atividade, 'liguepontos_detalhe') else '3' if hasattr(atividade, 'sequencia_detalhe') else ''

    # Atividades criadas pelo professor
    atv_quebracabeca = AtvQuebracabeca.query.filter_by(idAtividade=atividade.idAtividade).first()


    return render_template(
        'atividade.html',
        editar=True,
        atividade=atividade,
        profs=profs,
        atv_quebracabeca=atv_quebracabeca
    )



@atividade_bp.route('/excluiratividade/<int:id>')
def excluir_atividade(id):
    usuario = session.get('usuario', None)
    if not usuario or (usuario != 'admin' and usuario != 'professor'):
        return redirect(url_for('routes.home'))

    atividade = Atividade.query.get(id)

    if not atividade:
         print(f"Atividade com ID {id} não encontrada para exclusão.")
         return redirect(url_for('admin.admin_dashboard')) 

    # 1. Verificar e excluir detalhes específicos da atividade
    if atividade.quebracabeca_detalhe:
        # Obter o caminho da imagem antes de excluir o registro do banco de dados
        imagem_a_excluir = atividade.quebracabeca_detalhe.imagem_url
        
        # Excluir o registro do detalhe do quebra-cabeça do banco de dados
        db.session.delete(atividade.quebracabeca_detalhe)
        print(f"Detalhe de Quebra-cabeça para Atividade {id} excluído do banco de dados.")
        
        # Opcional: Excluir o arquivo físico da imagem
        if imagem_a_excluir:
            # Construir o caminho absoluto para o arquivo no sistema de arquivos
            # current_app.root_path é o caminho para a pasta 'app'
            # A URL no banco é 'static/uploads/nome_da_imagem.jpeg'
            # Então, combinamos root_path com a URL da imagem
            caminho_completo_arquivo = os.path.join(current_app.root_path, 'static', 'uploads', imagem_a_excluir)

            
            if os.path.exists(caminho_completo_arquivo):
                try:
                    os.remove(caminho_completo_arquivo)
                    print(f"Arquivo da imagem '{caminho_completo_arquivo}' excluído do servidor.")
                except OSError as e:
                    print(f"Erro ao excluir o arquivo da imagem '{caminho_completo_arquivo}': {e}")
            else:
                print(f"Aviso: Arquivo da imagem '{caminho_completo_arquivo}' não encontrado no servidor para exclusão.")

    # Adicione lógica semelhante para outros tipos de atividade (Ligue os pontos, Sequência)
    # se eles também tiverem arquivos associados que precisam ser excluídos.
    # Exemplo:
    # if atividade.liguepontos_detalhe:
    #     if atividade.liguepontos_detalhe.imagem_principal_url:
    #         caminho_completo_imagem_ligar_pontos = os.path.join(current_app.root_path, atividade.liguepontos_detalhe.imagem_principal_url.replace('/', os.sep))
    #         if os.path.exists(caminho_completo_imagem_ligar_pontos):
    #             try:
    #                 os.remove(caminho_completo_imagem_ligar_pontos)
    #                 print(f"Arquivo da imagem '{caminho_completo_imagem_ligar_pontos}' excluído.")
    #             except OSError as e:
    #                 print(f"Erro ao excluir o arquivo da imagem '{caminho_completo_imagem_ligar_pontos}': {e}")
    #     db.session.delete(atividade.liguepontos_detalhe)


    # 2. Excluir a atividade principal do banco de dados
    db.session.delete(atividade)
    db.session.commit() # Comita todas as exclusões

    print(f"Atividade {id} e seus detalhes foram excluídos com sucesso.")

    if usuario == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    else:
        return redirect(url_for('prof.prof_dashboard'))



@atividade_bp.route('/atribuiratividade', methods=['GET', 'POST'])
def atribuir_atividade():
    usuario = session.get('usuario', None)
    if not usuario or (usuario != 'admin' and usuario != 'professor'):
        return redirect(url_for('routes.home'))

    if request.method == 'POST':
        idTurma = request.form['turma']
        idAtividade = request.form['atividade']
        dataConclusao = request.form.get('dataConclusao') or None


        nova_atribuicao = TurmaAtividade(
            dataConclusao=dataConclusao,
            idAtividade=idAtividade,
            idTurma=idTurma
        )
        db.session.add(nova_atribuicao)
        db.session.commit()
        return redirect(url_for('prof.prof_dashboard'))

    turmas = Turma.query.filter_by(idProf=session['idProf']).all()
    atividades = Atividade.query.filter_by(idProf=session['idProf']).all()

    return render_template('atribuir.html', turmas=turmas, atividades=atividades)


@atividade_bp.route('/editaratribuiratividade/<int:idTurmaAtividade>', methods=['GET', 'POST'])
def editaratribuir_atividade(idTurmaAtividade):
    usuario = session.get('usuario', None)
    if not usuario or (usuario != 'admin' and usuario != 'professor'):
        return redirect(url_for('routes.home'))

    # Busca a atribuição que será editada ou retorna 404 caso não exista.
    atribuicao = TurmaAtividade.query.get_or_404(idTurmaAtividade)

    if request.method == 'POST':
        # Atualiza os campos da atribuição
        atribuicao.idTurma = request.form.get('turma')
        atribuicao.idAtividade = request.form.get('atividade')
        atribuicao.pontuacao = request.form.get('pontuacao') or None
        atribuicao.dataConclusao = request.form.get('dataConclusao') or None

        db.session.commit()
        return redirect(url_for('prof.prof_dashboard'))


    # Apenas turmas e atividades criadas pelo professor atual
    turmas = Turma.query.filter_by(idProf=session['idProf']).all()
    atividades = Atividade.query.filter_by(idProf=session['idProf']).all()

    return render_template('atribuir.html', editar=True, turmas=turmas, atividades=atividades, atribuicao=atribuicao)

@atividade_bp.route('/excluiratribuiratividade/<int:idTurmaAtividade>')
def excluiratribuir_atividade(idTurmaAtividade):
    usuario = session.get('usuario', None)
    if not usuario or (usuario != 'admin' and usuario != 'professor'):
        return redirect(url_for('routes.home'))

    atribuicao = TurmaAtividade.query.get_or_404(idTurmaAtividade)

    # Você pode validar se o professor atual é o dono da turma antes de excluir, se quiser reforçar a segurança:
    idProf = session.get('idProf')
    if usuario == 'professor' and atribuicao.turma.idProf != idProf:
        return "Acesso negado", 403

    db.session.delete(atribuicao)
    db.session.commit()
    return redirect(url_for('prof.prof_dashboard'))