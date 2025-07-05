from . import db
from sqlalchemy.sql import func # Para usar func.current_timestamp() como valor padrão no servidor

class Prof(db.Model):
    __tablename__ = 'prof' # Nome da tabela no banco de dados

    # Colunas da tabela 'prof'
    idProf = db.Column(db.Integer, primary_key=True, autoincrement=True) # Chave primária, auto-incrementável
    nome = db.Column(db.String(50), nullable=False) # Nome do professor, não pode ser nulo
    login = db.Column(db.String(30), unique=True, nullable=False) # Login único para o professor, não pode ser nulo
    senha = db.Column(db.String(255), nullable=False) # Senha do professor (armazenar hash), não pode ser nula
    status = db.Column(db.Integer, nullable=False) # Status do professor (ex: 1 para ativo, 0 para inativo)
    dataCadastro = db.Column(db.TIMESTAMP, nullable=False, server_default=func.current_timestamp()) # Data e hora do cadastro, padrão é o timestamp atual

    # Relacionamentos
    # 'turmas' permite acessar todas as turmas criadas por este professor
    # 'prof' será o atributo na classe Turma para acessar este professor
    turmas = db.relationship('Turma', backref='prof', lazy=True)
    # 'atividades_criadas' permite acessar todas as atividades criadas por este professor
    # 'criador_prof' será o atributo na classe Atividade para acessar este professor
    atividades_criadas = db.relationship('Atividade', backref='criador_prof', lazy=True)

    def __repr__(self):
        return f'<Prof {self.idProf}: {self.nome}>' # Representação em string do objeto

class Turma(db.Model):
    __tablename__ = 'turma' # Nome da tabela no banco de dados

    # Colunas da tabela 'turma'
    idTurma = db.Column(db.Integer, primary_key=True, autoincrement=True) # Chave primária, auto-incrementável
    nome = db.Column(db.String(45), nullable=False) # Nome da turma, não pode ser nulo
    descricao = db.Column(db.Text, nullable=False) # Descrição da turma, não pode ser nula
    idProf = db.Column(db.Integer, db.ForeignKey('prof.idProf'), nullable=False) # Chave estrangeira referenciando Prof.idProf

    # Relacionamentos
    # 'alunos' permite acessar todos os alunos desta turma
    # 'turma' será o atributo na classe Aluno para acessar esta turma
    alunos = db.relationship('Aluno', backref='turma', lazy=True)
    # 'atividades_associadas' permite acessar as associações TurmaAtividade desta turma
    # 'turma' será o atributo na classe TurmaAtividade para acessar esta turma
    # 'lazy="dynamic"' retorna um query object, útil para filtros adicionais
    atividades_associadas = db.relationship('TurmaAtividade', backref='turma', lazy='dynamic')

    def __repr__(self):
        return f'<Turma {self.idTurma}: {self.nome}>' # Representação em string do objeto

class Aluno(db.Model):
    __tablename__ = 'aluno' # Nome da tabela no banco de dados

    # Colunas da tabela 'aluno'
    idAluno = db.Column(db.Integer, primary_key=True, autoincrement=True) # Chave primária, auto-incrementável
    nome = db.Column(db.String(50), nullable=False) # Nome do aluno, não pode ser nulo
    login = db.Column(db.String(30), unique=True, nullable=False) # Login único para o aluno, não pode ser nulo
    senha = db.Column(db.String(255), nullable=False) # Senha do aluno (armazenar hash), não pode ser nula
    dataNascimento = db.Column(db.Date, nullable=False) # Data de nascimento do aluno
    dataCadastro = db.Column(db.TIMESTAMP, nullable=False, server_default=func.current_timestamp()) # Data e hora do cadastro, padrão é o timestamp atual
    ultimologin = db.Column(db.TIMESTAMP, nullable=True) # Data e hora do último login do aluno. Considerar server_default=func.now() ou nullable=True dependendo da lógica de atualização.
    pontuacao_total = db.Column(db.Integer, nullable=False, default=0) # Pontuação total do aluno, padrão 0
    status = db.Column(db.Integer, nullable=False, default=1) # Status do aluno (ex: 1 para ativo, 0 para inativo), padrão 1
    idTurma = db.Column(db.Integer, db.ForeignKey('turma.idTurma'), nullable=False) # Chave estrangeira referenciando turma.idTurma

    # O relacionamento reverso 'turma' já é criado pelo backref em Turma.alunos

    def __repr__(self):
        return f'<Aluno {self.idAluno}: {self.nome}>' # Representação em string do objeto

class Atividade(db.Model):
    __tablename__ = 'atividade' # Nome da tabela no banco de dados

    # Colunas da tabela 'atividade'
    idAtividade = db.Column(db.Integer, primary_key=True, autoincrement=True) # Chave primária, auto-incrementável
    titulo = db.Column(db.String(30), nullable=False) # Título da atividade, não pode ser nulo
    descricao = db.Column(db.Text, nullable=False) # Descrição da atividade, não pode ser nula
    nivel = db.Column(db.String(45), nullable=False) # Nível de dificuldade da atividade (ex: Fácil, Médio, Difícil)
    tipo = db.Column(db.String(45), nullable=False) # Tipo da atividade (ex: Quebra-cabeça, Ligue os pontos, ...)
    idProf = db.Column(db.Integer, db.ForeignKey('prof.idProf'), nullable=False) # Chave estrangeira referenciando Prof.idProf (professor que criou)

    # Relacionamentos
    # 'turmas_associadas' permite acessar as associações TurmaAtividade desta atividade
    # 'atividade' será o atributo na classe TurmaAtividade para acessar esta atividade
    # 'lazy="dynamic"' retorna um query object
    turmas_associadas = db.relationship('TurmaAtividade', backref='atividade', lazy='dynamic', cascade="all, delete-orphan")

    # Relacionamentos para tipos específicos de atividade (um-para-um)
    # 'uselist=False' indica que é um relacionamento um-para-um (ou um-para-zero)
    # 'atividade_base' será o atributo no modelo específico (ex: AtvQuebracabeca) para acessar esta Atividade genérica
    quebracabeca_detalhe = db.relationship('AtvQuebracabeca', backref='atividade_base', uselist=False, lazy=True, cascade="all, delete-orphan")
    liguepontos_detalhe = db.relationship('AtvLiguepontos', backref='atividade_base', uselist=False, lazy=True, cascade="all, delete-orphan")
    sequencia_detalhe = db.relationship('AtvSequencia', backref='atividade_base', uselist=False, lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Atividade {self.idAtividade}: {self.titulo}>' # Representação em string do objeto

class TurmaAtividade(db.Model): # Tabela de associação com dados extras
    __tablename__ = 'turma_atividade' # Nome da tabela no banco de dados

    # Colunas da tabela 'turma_atividade'
    idTurmaAtividade = db.Column(db.Integer, primary_key=True, autoincrement=True) # Chave primária, auto-incrementável
    dataAtribuicao = db.Column(db.TIMESTAMP, nullable=True, server_default=func.current_timestamp()) # Data e hora em que a atividade foi atribuída à turma
    dataConclusao = db.Column(db.DateTime, nullable=True) # Data e hora de conclusão. Pode ser nulo se ainda não concluída.
    
    idAtividade = db.Column(db.Integer, db.ForeignKey('atividade.idAtividade', ondelete='CASCADE'), nullable=False) # FK para atividade.idAtividade
    idTurma = db.Column(db.Integer, db.ForeignKey('turma.idTurma'), nullable=False) # FK para turma.idTurma

    # Os relacionamentos reversos 'turma' e 'atividade' já são criados pelos backrefs em Turma e Atividade respectivamente.

    def __repr__(self):
        return f'<TurmaAtividade {self.idTurmaAtividade} (Turma:{self.idTurma}-Ativ:{self.idAtividade})>' # Representação em string


class AlunoAtividade(db.Model):
    __tablename__ = 'aluno_atividade'  # Nome da tabela no banco de dados

    idAluno_atividade = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Chave primária
    tempo_segundos = db.Column(db.Integer, nullable=True)  # Tempo que o aluno levou na atividade (em segundos)
    pontuacao = db.Column(db.Integer, nullable=True)  # Pontuação obtida
    data_jogada = db.Column(db.TIMESTAMP, nullable=False, server_default=func.current_timestamp())  # Quando foi jogado
    tentativa = db.Column(db.Integer, nullable=False) 
    # FKs
    idAluno = db.Column(db.Integer, db.ForeignKey('aluno.idAluno'), nullable=False)
    idTurmaAtividade = db.Column(db.Integer, db.ForeignKey('turma_atividade.idTurmaAtividade'), nullable=False)

    # Relacionamentos reversos
    aluno = db.relationship('Aluno', backref=db.backref('atividades_jogadas', lazy=True))
    turma_atividade = db.relationship(
        'TurmaAtividade',
        backref=db.backref('jogos_realizados', lazy=True, cascade="all, delete-orphan")
    )

    def __repr__(self):
        return f'<AlunoAtividade {self.idAluno_atividade} (Aluno:{self.idAluno} - TurmaAtiv:{self.idTurmaAtividade})>'


class AtvQuebracabeca(db.Model):
    __tablename__ = 'atv_quebracabeca' # Nome da tabela no banco de dados

    # Colunas da tabela 'atv_quebracabeca'
    idatv_quebracabeca = db.Column(db.Integer, primary_key=True, autoincrement=True) # Chave primária
    imagem_url = db.Column(db.String(255), nullable=False) # URL da imagem principal do quebra-cabeça
    # Chave estrangeira para 'atividade.idAtividade'.
    # 'unique=True' garante que uma Atividade só pode ter um detalhe de AtvQuebracabeca (relacionamento 1-para-1).
    idAtividade = db.Column(db.Integer, db.ForeignKey('atividade.idAtividade'), nullable=False, unique=True)

    # O relacionamento reverso 'atividade_base' já é criado pelo backref em Atividade.quebracabeca_detalhe

    def __repr__(self):
        return f'<AtvQuebracabeca {self.idatv_quebracabeca}: {self.nome}>' # Representação em string

class AtvLiguepontos(db.Model):
    __tablename__ = 'atv_liguepontos' # Nome da tabela no banco de dados

    # Colunas da tabela 'atv_liguepontos'
    idatv_liguepontos = db.Column(db.Integer, primary_key=True, autoincrement=True) # Chave primária
    nome = db.Column(db.String(45), nullable=False) # Nome específico da atividade de ligar pontos
    # Chave estrangeira para 'atividade.idAtividade'.
    # 'unique=True' garante que uma Atividade só pode ter um detalhe de AtvLiguepontos (relacionamento 1-para-1).
    idAtividade = db.Column(db.Integer, db.ForeignKey('atividade.idAtividade'), nullable=False, unique=True)

    # Relacionamento
    # 'pares_itens' permite acessar todos os pares desta atividade de ligar pontos
    # 'liguepontos_atividade' será o atributo na classe Pares para acessar esta AtvLiguepontos
    pares_itens = db.relationship('Pares', backref='liguepontos_atividade', lazy=True)
    # O relacionamento reverso 'atividade_base' já é criado pelo backref em Atividade.liguepontos_detalhe

    def __repr__(self):
        return f'<AtvLiguepontos {self.idatv_liguepontos}: {self.nome}>' # Representação em string

class Pares(db.Model):
    __tablename__ = 'pares' # Nome da tabela no banco de dados

    # Colunas da tabela 'pares'
    idPares = db.Column(db.Integer, primary_key=True, autoincrement=True) # Chave primária
    descricao = db.Column(db.String(45), nullable=False) # Descrição do par (ex: "Maçã", "Número 1")
    imagem_url = db.Column(db.String(255), nullable=False) # URL da imagem para este item do par
    # Chave estrangeira para 'atv_liguepontos.idatv_liguepontos'
    idatv_liguepontos = db.Column(db.Integer, db.ForeignKey('atv_liguepontos.idatv_liguepontos'), nullable=False)

    # O relacionamento reverso 'liguepontos_atividade' já é criado pelo backref em AtvLiguepontos.pares_itens

    def __repr__(self):
        return f'<Pares {self.idPares}: {self.descricao}>' # Representação em string

class AtvSequencia(db.Model):
    __tablename__ = 'atv_sequencia' # Nome da tabela no banco de dados

    # Colunas da tabela 'atv_sequencia'
    idatv_sequencia = db.Column(db.Integer, primary_key=True, autoincrement=True) # Chave primária
    nome = db.Column(db.String(45), nullable=False) # Nome específico da atividade de sequência
    # Chave estrangeira para 'atividade.idAtividade'.
    # 'unique=True' garante que uma Atividade só pode ter um detalhe de AtvSequencia (relacionamento 1-para-1).
    idAtividade = db.Column(db.Integer, db.ForeignKey('atividade.idAtividade'), nullable=False, unique=True)

    # Relacionamento
    # 'sequencia_itens' permite acessar todos os itens desta atividade de sequência
    # 'sequencia_atividade' será o atributo na classe SequenciaItem para acessar esta AtvSequencia
    sequencia_itens = db.relationship('SequenciaItem', backref='sequencia_atividade', lazy=True)
    # O relacionamento reverso 'atividade_base' já é criado pelo backref em Atividade.sequencia_detalhe

    def __repr__(self):
        return f'<AtvSequencia {self.idatv_sequencia}: {self.nome}>' # Representação em string

class SequenciaItem(db.Model): # Renomeado de Sequencia para SequenciaItem para maior clareza
    __tablename__ = 'sequencia' # Nome da tabela no banco de dados

    # Colunas da tabela 'sequencia'
    idSequencia = db.Column(db.Integer, primary_key=True, autoincrement=True) # Chave primária
    descricao = db.Column(db.String(45), nullable=False) # Descrição do item da sequência
    imagem_url = db.Column(db.String(255), nullable=False) # URL da imagem para este item da sequência
    ordem = db.Column(db.Integer, nullable=False) # Ordem do item na sequência
    # Chave estrangeira para 'atv_sequencia.idatv_sequencia'
    idatv_sequencia = db.Column(db.Integer, db.ForeignKey('atv_sequencia.idatv_sequencia'), nullable=False)

    # O relacionamento reverso 'sequencia_atividade' já é criado pelo backref em AtvSequencia.sequencia_itens

    def __repr__(self):
        return f'<SequenciaItem {self.idSequencia}: Ordem {self.ordem} - {self.descricao}>' # Representação em string