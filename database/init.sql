-- ============================================
-- SmartFat - Script de Inicialização do Banco
-- ============================================

CREATE DATABASE IF NOT EXISTS smartfat;
USE smartfat;

-- Tabela de usuários do sistema (admin, professor)
CREATE TABLE IF NOT EXISTS usuarios (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nome     VARCHAR(100) NOT NULL,
    email    VARCHAR(100) NOT NULL UNIQUE,
    senha    VARCHAR(255) NOT NULL,
    perfil   ENUM('admin', 'professor', 'recepcionista') DEFAULT 'recepcionista'
);

-- Planos disponíveis na academia
CREATE TABLE IF NOT EXISTS planos (
    idPlano  INT AUTO_INCREMENT PRIMARY KEY,
    nome     VARCHAR(100) NOT NULL,
    valor    DECIMAL(6,2) NOT NULL,
    duracao  INT DEFAULT 30
);

-- Alunos cadastrados
CREATE TABLE IF NOT EXISTS alunos (
    idAluno       INT AUTO_INCREMENT PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL,
    CPF           VARCHAR(100) NOT NULL UNIQUE,
    telefone      VARCHAR(11),
    status        VARCHAR(45) DEFAULT 'Ativo',
    Treino_idTreino         INT,
    AvaliacaoFisica_idAvaliacaoFisica INT,
    Plano_idPlano INT,
    FOREIGN KEY (Plano_idPlano) REFERENCES planos(idPlano)
);

-- Relatório Operacional (referenciado por Acesso)
CREATE TABLE IF NOT EXISTS relatorios_operacionais (
    idRelatorioOperacional INT AUTO_INCREMENT PRIMARY KEY,
    frequenciaMensal       INT,
    quantAulas             INT,
    Aluno_idAluno          INT,
    FOREIGN KEY (Aluno_idAluno) REFERENCES alunos(idAluno)
);

-- Controle de acesso à academia
CREATE TABLE IF NOT EXISTS acessos (
    idAcesso               INT AUTO_INCREMENT PRIMARY KEY,
    dataHoraEntrada        DATETIME,
    dataHoraSaida          DATETIME,
    RelatorioOperacional_idRelatorioOperacional INT,
    Aluno_idAluno          INT NOT NULL,
    Aluno_Treino_idTreino  INT,
    Aluno_AvaliacaoFisica_idAvaliacaoFisica INT,
    Aluno_Plano_idPlano    INT,
    FOREIGN KEY (Aluno_idAluno) REFERENCES alunos(idAluno)
);

-- Avaliações físicas dos alunos
CREATE TABLE IF NOT EXISTS avaliacoes_fisicas (
    idAvaliacaoFisica INT AUTO_INCREMENT PRIMARY KEY,
    peso              DOUBLE,
    altura            DOUBLE,
    Aluno_idAluno     INT,
    FOREIGN KEY (Aluno_idAluno) REFERENCES alunos(idAluno)
);

-- Treinos associados a alunos
CREATE TABLE IF NOT EXISTS treinos (
    idTreino      INT AUTO_INCREMENT PRIMARY KEY,
    descricao     VARCHAR(100),
    data          DATE,
    Aluno_idTreino INT,
    FOREIGN KEY (Aluno_idTreino) REFERENCES alunos(idAluno)
);

-- Relatório financeiro por período
CREATE TABLE IF NOT EXISTS relatorios_financeiros (
    idRelatorioFinanceiro INT AUTO_INCREMENT PRIMARY KEY,
    periodo               INT,
    totalReceita          DECIMAL(10,2)
);

-- Módulo Financeiro (centro de custo)
CREATE TABLE IF NOT EXISTS financeiros (
    idFinanceiro INT AUTO_INCREMENT PRIMARY KEY,
    valor        DECIMAL(6,2),
    dataPagamento DATE,
    RelatorioFinanceiro_idRelatorioFinanceiro INT,
    FOREIGN KEY (RelatorioFinanceiro_idRelatorioFinanceiro) REFERENCES relatorios_financeiros(idRelatorioFinanceiro)
);

-- Mensalidades dos alunos
CREATE TABLE IF NOT EXISTS mensalidades (
    idMensalidade      INT AUTO_INCREMENT PRIMARY KEY,
    valor              DECIMAL(6,2) NOT NULL,
    dataVencimento     DATE,
    status             VARCHAR(45) DEFAULT 'Pendente',
    Aluno_idAluno      INT NOT NULL,
    Financeiro_idFinanceiro INT,
    FOREIGN KEY (Aluno_idAluno) REFERENCES alunos(idAluno),
    FOREIGN KEY (Financeiro_idFinanceiro) REFERENCES financeiros(idFinanceiro)
);

-- ============================================
-- Dados iniciais (seed)
-- ============================================

INSERT INTO usuarios (nome, email, senha, perfil) VALUES
-- Senha: admin123 (bcrypt hash)
('Administrador', 'admin@smartfat.com', '$2b$12$FAd/aQKomqavdY2mcmLJfeihXtgPb64Vbh09vfCQLE8lq5JvvnIUm', 'admin');

INSERT INTO planos (nome, valor, duracao) VALUES
('Mensal Básico', 89.90, 30),
('Mensal Plus', 129.90, 30),
('Trimestral', 299.90, 90),
('Semestral', 529.90, 180),
('Anual', 899.90, 365);

INSERT INTO alunos (nome, CPF, telefone, status, Plano_idPlano) VALUES
('João Silva',    '111.111.111-11', '27999990001', 'Ativo', 1),
('Maria Souza',   '222.222.222-22', '27999990002', 'Ativo', 2),
('Pedro Almeida', '333.333.333-33', '27999990003', 'Ativo', 3),
('Ana Costa',     '444.444.444-44', '27999990004', 'Inativo', 1);

INSERT INTO financeiros (valor, dataPagamento) VALUES (0, CURDATE());

INSERT INTO mensalidades (valor, dataVencimento, status, Aluno_idAluno, Financeiro_idFinanceiro) VALUES
(89.90,  DATE_ADD(CURDATE(), INTERVAL 10 DAY),  'Pendente', 1, 1),
(129.90, DATE_ADD(CURDATE(), INTERVAL -5 DAY),  'Pago',     2, 1),
(299.90, DATE_ADD(CURDATE(), INTERVAL 20 DAY),  'Pendente', 3, 1),
(89.90,  DATE_ADD(CURDATE(), INTERVAL -30 DAY), 'Pendente', 4, 1);
