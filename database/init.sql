-- ============================================
-- SmartFat - Script de Inicialização do Banco
-- ============================================

CREATE DATABASE IF NOT EXISTS smartfat;
USE smartfat;

-- Tabela de usuários do sistema (admin, treinador, aluno)
CREATE TABLE IF NOT EXISTS usuarios (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nome     VARCHAR(100) NOT NULL,
    email    VARCHAR(100) NOT NULL UNIQUE,
    senha    VARCHAR(255) NOT NULL,
    perfil   ENUM('admin', 'treinador', 'professor', 'aluno', 'recepcionista') DEFAULT 'recepcionista',
    Aluno_idAluno INT NULL
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
    permitido              TINYINT(1) DEFAULT 1,
    motivoNegacao          VARCHAR(255),
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

INSERT INTO usuarios (nome, email, senha, perfil, Aluno_idAluno) VALUES
-- Senha: admin123 (bcrypt hash)
('Administrador', 'admin@smartfat.com', '$2b$12$FAd/aQKomqavdY2mcmLJfeihXtgPb64Vbh09vfCQLE8lq5JvvnIUm', 'admin', NULL),
-- Senha: treinador123
('Treinador SmartFat', 'treinador@smartfat.com', '$2b$12$MkhwDzmvp6cSiOZFy0i3VuAJbPGVrDMkOXa9KiDVcmVIVJdA1kd5i', 'treinador', NULL),
-- Senha: aluno123
('Lucas Martins', 'aluno@smartfat.com', '$2b$12$54BL.9j3uUvPxIgybkPIR.5NyvcDoHeQRsOOkrc1cEiI07KhaHMOW', 'aluno', 5),
('Fernanda Lima', 'fernanda@smartfat.com', '$2b$12$54BL.9j3uUvPxIgybkPIR.5NyvcDoHeQRsOOkrc1cEiI07KhaHMOW', 'aluno', 6),
('Bianca Rocha', 'bianca@smartfat.com', '$2b$12$54BL.9j3uUvPxIgybkPIR.5NyvcDoHeQRsOOkrc1cEiI07KhaHMOW', 'aluno', 8);

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
('Ana Costa',     '444.444.444-44', '27999990004', 'Inativo', 1),
('Lucas Martins', '555.555.555-55', '27999990005', 'Ativo', 1),
('Fernanda Lima', '666.666.666-66', '27999990006', 'Ativo', 2),
('Rafael Gomes',  '777.777.777-77', '27999990007', 'Ativo', 4),
('Bianca Rocha',  '888.888.888-88', '27999990008', 'Ativo', 5),
('Thiago Nunes',  '999.999.999-99', '27999990009', 'Ativo', 1),
('Camila Ribeiro','101.101.101-10', '27999990010', 'Inativo', 2),
('Diego Santos',  '202.202.202-20', '27999990011', 'Ativo', 3),
('Larissa Alves', '303.303.303-30', '27999990012', 'Ativo', 1),
('Marcos Vieira', '404.404.404-40', '27999990013', 'Ativo', 4),
('Patricia Melo', '505.505.505-50', '27999990014', 'Ativo', 2),
('Bruno Castro',  '606.606.606-60', '27999990015', 'Inativo', 1);

INSERT INTO financeiros (valor, dataPagamento) VALUES (0, CURDATE());

INSERT INTO mensalidades (valor, dataVencimento, status, Aluno_idAluno, Financeiro_idFinanceiro) VALUES
(89.90,  DATE_ADD(CURDATE(), INTERVAL 10 DAY),  'Pendente', 1, 1),
(129.90, DATE_ADD(CURDATE(), INTERVAL -5 DAY),  'Pago',     2, 1),
(299.90, DATE_ADD(CURDATE(), INTERVAL 20 DAY),  'Pendente', 3, 1),
(89.90,  DATE_ADD(CURDATE(), INTERVAL -30 DAY), 'Pendente', 4, 1),
(89.90,  DATE_ADD(CURDATE(), INTERVAL -7 DAY),  'Pendente', 5, 1),
(129.90, DATE_ADD(CURDATE(), INTERVAL 12 DAY),  'Pendente', 6, 1),
(529.90, DATE_ADD(CURDATE(), INTERVAL -2 DAY),  'Pago',     7, 1),
(899.90, DATE_ADD(CURDATE(), INTERVAL 40 DAY),  'Pendente', 8, 1),
(89.90,  DATE_ADD(CURDATE(), INTERVAL -12 DAY), 'Pendente', 9, 1),
(129.90, DATE_ADD(CURDATE(), INTERVAL -20 DAY), 'Pendente', 10, 1),
(299.90, DATE_ADD(CURDATE(), INTERVAL 25 DAY),  'Pendente', 11, 1),
(89.90,  DATE_ADD(CURDATE(), INTERVAL -1 DAY),  'Pago',     12, 1),
(529.90, DATE_ADD(CURDATE(), INTERVAL 18 DAY),  'Pendente', 13, 1),
(129.90, DATE_ADD(CURDATE(), INTERVAL 5 DAY),   'Pendente', 14, 1),
(89.90,  DATE_ADD(CURDATE(), INTERVAL -45 DAY), 'Pendente', 15, 1),
(89.90,  DATE_ADD(CURDATE(), INTERVAL -35 DAY), 'Pago',     1, 1),
(129.90, DATE_ADD(CURDATE(), INTERVAL -32 DAY), 'Pago',     6, 1),
(299.90, DATE_ADD(CURDATE(), INTERVAL -15 DAY), 'Pago',     11, 1);

INSERT INTO treinos (descricao, data, Aluno_idTreino) VALUES
('Treino A - membros superiores', CURDATE(), 5),
('Treino B - membros inferiores', DATE_ADD(CURDATE(), INTERVAL 2 DAY), 5),
('Full body iniciante', DATE_ADD(CURDATE(), INTERVAL -3 DAY), 1),
('Hipertrofia superiores', DATE_ADD(CURDATE(), INTERVAL -2 DAY), 2),
('Cardio e mobilidade', DATE_ADD(CURDATE(), INTERVAL -1 DAY), 3),
('Forca pernas', CURDATE(), 6),
('Core e estabilidade', DATE_ADD(CURDATE(), INTERVAL 1 DAY), 7),
('Resistencia funcional', DATE_ADD(CURDATE(), INTERVAL 2 DAY), 8),
('Treino de retorno leve', DATE_ADD(CURDATE(), INTERVAL -5 DAY), 9),
('Condicionamento HIIT', DATE_ADD(CURDATE(), INTERVAL 3 DAY), 11),
('Mobilidade e postura', DATE_ADD(CURDATE(), INTERVAL 4 DAY), 12),
('Forca total', DATE_ADD(CURDATE(), INTERVAL 5 DAY), 13),
('Hipertrofia inferiores', DATE_ADD(CURDATE(), INTERVAL 6 DAY), 14),
('Reabilitacao leve', DATE_ADD(CURDATE(), INTERVAL -10 DAY), 15);

INSERT INTO avaliacoes_fisicas (peso, altura, Aluno_idAluno) VALUES
(82.5, 1.78, 1),
(64.2, 1.65, 2),
(91.0, 1.82, 3),
(74.8, 1.74, 5),
(59.7, 1.62, 6),
(88.4, 1.80, 7),
(70.1, 1.68, 8),
(96.3, 1.85, 9),
(77.9, 1.76, 11),
(61.5, 1.64, 12),
(84.0, 1.79, 13),
(68.6, 1.70, 14);

INSERT INTO acessos (dataHoraEntrada, dataHoraSaida, permitido, motivoNegacao, Aluno_idAluno) VALUES
(DATE_SUB(NOW(), INTERVAL 8 DAY), DATE_SUB(NOW(), INTERVAL 8 DAY) + INTERVAL 75 MINUTE, 1, NULL, 1),
(DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY) + INTERVAL 68 MINUTE, 1, NULL, 2),
(DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY) + INTERVAL 60 MINUTE, 1, NULL, 3),
(DATE_SUB(NOW(), INTERVAL 5 DAY), NULL, 0, 'Cadastro do aluno esta inativo.', 4),
(DATE_SUB(NOW(), INTERVAL 4 DAY), NULL, 0, 'Mensalidade vencida.', 5),
(DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY) + INTERVAL 55 MINUTE, 1, NULL, 6),
(DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY) + INTERVAL 80 MINUTE, 1, NULL, 7),
(DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY) + INTERVAL 70 MINUTE, 1, NULL, 8),
(NOW(), NULL, 0, 'Mensalidade vencida.', 9),
(NOW(), DATE_ADD(NOW(), INTERVAL 50 MINUTE), 1, NULL, 11),
(DATE_SUB(NOW(), INTERVAL 12 HOUR), DATE_SUB(NOW(), INTERVAL 11 HOUR), 1, NULL, 12),
(DATE_SUB(NOW(), INTERVAL 6 HOUR), DATE_SUB(NOW(), INTERVAL 5 HOUR), 1, NULL, 13),
(DATE_SUB(NOW(), INTERVAL 3 HOUR), DATE_SUB(NOW(), INTERVAL 2 HOUR), 1, NULL, 14),
(DATE_SUB(NOW(), INTERVAL 2 HOUR), NULL, 0, 'Cadastro do aluno esta inativo.', 15);
