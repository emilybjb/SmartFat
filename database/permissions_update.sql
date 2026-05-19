USE smartfat;

ALTER TABLE usuarios
    ADD COLUMN IF NOT EXISTS Aluno_idAluno INT NULL,
    MODIFY perfil ENUM('admin', 'treinador', 'professor', 'aluno', 'recepcionista') DEFAULT 'recepcionista';

ALTER TABLE acessos
    ADD COLUMN IF NOT EXISTS permitido TINYINT(1) DEFAULT 1,
    ADD COLUMN IF NOT EXISTS motivoNegacao VARCHAR(255);

INSERT IGNORE INTO alunos (idAluno, nome, CPF, telefone, status, Plano_idPlano) VALUES
(5, 'Lucas Martins', '555.555.555-55', '27999990005', 'Ativo', 1),
(6, 'Fernanda Lima', '666.666.666-66', '27999990006', 'Ativo', 2),
(7, 'Rafael Gomes', '777.777.777-77', '27999990007', 'Ativo', 4),
(8, 'Bianca Rocha', '888.888.888-88', '27999990008', 'Ativo', 5),
(9, 'Thiago Nunes', '999.999.999-99', '27999990009', 'Ativo', 1),
(10, 'Camila Ribeiro', '101.101.101-10', '27999990010', 'Inativo', 2),
(11, 'Diego Santos', '202.202.202-20', '27999990011', 'Ativo', 3),
(12, 'Larissa Alves', '303.303.303-30', '27999990012', 'Ativo', 1),
(13, 'Marcos Vieira', '404.404.404-40', '27999990013', 'Ativo', 4),
(14, 'Patricia Melo', '505.505.505-50', '27999990014', 'Ativo', 2),
(15, 'Bruno Castro', '606.606.606-60', '27999990015', 'Inativo', 1);

INSERT IGNORE INTO usuarios (nome, email, senha, perfil, Aluno_idAluno) VALUES
('Treinador SmartFat', 'treinador@smartfat.com', '$2b$12$MkhwDzmvp6cSiOZFy0i3VuAJbPGVrDMkOXa9KiDVcmVIVJdA1kd5i', 'treinador', NULL),
('Lucas Martins', 'aluno@smartfat.com', '$2b$12$54BL.9j3uUvPxIgybkPIR.5NyvcDoHeQRsOOkrc1cEiI07KhaHMOW', 'aluno', 5),
('Fernanda Lima', 'fernanda@smartfat.com', '$2b$12$54BL.9j3uUvPxIgybkPIR.5NyvcDoHeQRsOOkrc1cEiI07KhaHMOW', 'aluno', 6),
('Bianca Rocha', 'bianca@smartfat.com', '$2b$12$54BL.9j3uUvPxIgybkPIR.5NyvcDoHeQRsOOkrc1cEiI07KhaHMOW', 'aluno', 8);

INSERT INTO mensalidades (valor, dataVencimento, status, Aluno_idAluno, Financeiro_idFinanceiro)
SELECT 89.90, DATE_ADD(CURDATE(), INTERVAL -7 DAY), 'Pendente', 5, 1
WHERE NOT EXISTS (
    SELECT 1 FROM mensalidades
    WHERE Aluno_idAluno = 5 AND status = 'Pendente' AND dataVencimento < CURDATE()
);

INSERT INTO mensalidades (valor, dataVencimento, status, Aluno_idAluno, Financeiro_idFinanceiro)
SELECT valor, vencimento, status, aluno_id, 1
FROM (
    SELECT 129.90 valor, DATE_ADD(CURDATE(), INTERVAL 12 DAY) vencimento, 'Pendente' status, 6 aluno_id
    UNION ALL SELECT 529.90, DATE_ADD(CURDATE(), INTERVAL -2 DAY), 'Pago', 7
    UNION ALL SELECT 899.90, DATE_ADD(CURDATE(), INTERVAL 40 DAY), 'Pendente', 8
    UNION ALL SELECT 89.90, DATE_ADD(CURDATE(), INTERVAL -12 DAY), 'Pendente', 9
    UNION ALL SELECT 129.90, DATE_ADD(CURDATE(), INTERVAL -20 DAY), 'Pendente', 10
    UNION ALL SELECT 299.90, DATE_ADD(CURDATE(), INTERVAL 25 DAY), 'Pendente', 11
    UNION ALL SELECT 89.90, DATE_ADD(CURDATE(), INTERVAL -1 DAY), 'Pago', 12
    UNION ALL SELECT 529.90, DATE_ADD(CURDATE(), INTERVAL 18 DAY), 'Pendente', 13
    UNION ALL SELECT 129.90, DATE_ADD(CURDATE(), INTERVAL 5 DAY), 'Pendente', 14
    UNION ALL SELECT 89.90, DATE_ADD(CURDATE(), INTERVAL -45 DAY), 'Pendente', 15
) mensalidades_seed
WHERE NOT EXISTS (
    SELECT 1 FROM mensalidades m
    WHERE m.Aluno_idAluno = mensalidades_seed.aluno_id
);

INSERT INTO treinos (descricao, data, Aluno_idTreino)
SELECT 'Treino A - membros superiores', CURDATE(), 5
WHERE NOT EXISTS (
    SELECT 1 FROM treinos WHERE Aluno_idTreino = 5 AND descricao = 'Treino A - membros superiores'
);

INSERT INTO treinos (descricao, data, Aluno_idTreino)
SELECT 'Treino B - membros inferiores', DATE_ADD(CURDATE(), INTERVAL 2 DAY), 5
WHERE NOT EXISTS (
    SELECT 1 FROM treinos WHERE Aluno_idTreino = 5 AND descricao = 'Treino B - membros inferiores'
);

INSERT INTO treinos (descricao, data, Aluno_idTreino)
SELECT descricao, data_treino, aluno_id
FROM (
    SELECT 'Full body iniciante' descricao, DATE_ADD(CURDATE(), INTERVAL -3 DAY) data_treino, 1 aluno_id
    UNION ALL SELECT 'Hipertrofia superiores', DATE_ADD(CURDATE(), INTERVAL -2 DAY), 2
    UNION ALL SELECT 'Cardio e mobilidade', DATE_ADD(CURDATE(), INTERVAL -1 DAY), 3
    UNION ALL SELECT 'Forca pernas', CURDATE(), 6
    UNION ALL SELECT 'Core e estabilidade', DATE_ADD(CURDATE(), INTERVAL 1 DAY), 7
    UNION ALL SELECT 'Resistencia funcional', DATE_ADD(CURDATE(), INTERVAL 2 DAY), 8
    UNION ALL SELECT 'Treino de retorno leve', DATE_ADD(CURDATE(), INTERVAL -5 DAY), 9
    UNION ALL SELECT 'Condicionamento HIIT', DATE_ADD(CURDATE(), INTERVAL 3 DAY), 11
    UNION ALL SELECT 'Mobilidade e postura', DATE_ADD(CURDATE(), INTERVAL 4 DAY), 12
    UNION ALL SELECT 'Forca total', DATE_ADD(CURDATE(), INTERVAL 5 DAY), 13
    UNION ALL SELECT 'Hipertrofia inferiores', DATE_ADD(CURDATE(), INTERVAL 6 DAY), 14
    UNION ALL SELECT 'Reabilitacao leve', DATE_ADD(CURDATE(), INTERVAL -10 DAY), 15
) treinos_seed
WHERE NOT EXISTS (
    SELECT 1 FROM treinos t
    WHERE t.Aluno_idTreino = treinos_seed.aluno_id
      AND t.descricao = treinos_seed.descricao
);

INSERT INTO avaliacoes_fisicas (peso, altura, Aluno_idAluno)
SELECT peso, altura, aluno_id
FROM (
    SELECT 82.5 peso, 1.78 altura, 1 aluno_id
    UNION ALL SELECT 64.2, 1.65, 2
    UNION ALL SELECT 91.0, 1.82, 3
    UNION ALL SELECT 74.8, 1.74, 5
    UNION ALL SELECT 59.7, 1.62, 6
    UNION ALL SELECT 88.4, 1.80, 7
    UNION ALL SELECT 70.1, 1.68, 8
    UNION ALL SELECT 96.3, 1.85, 9
    UNION ALL SELECT 77.9, 1.76, 11
    UNION ALL SELECT 61.5, 1.64, 12
    UNION ALL SELECT 84.0, 1.79, 13
    UNION ALL SELECT 68.6, 1.70, 14
) avaliacoes_seed
WHERE NOT EXISTS (
    SELECT 1 FROM avaliacoes_fisicas av
    WHERE av.Aluno_idAluno = avaliacoes_seed.aluno_id
);

INSERT INTO acessos (dataHoraEntrada, dataHoraSaida, permitido, motivoNegacao, Aluno_idAluno)
SELECT entrada, saida, permitido, motivo, aluno_id
FROM (
    SELECT DATE_SUB(NOW(), INTERVAL 8 DAY) entrada, DATE_SUB(NOW(), INTERVAL 8 DAY) + INTERVAL 75 MINUTE saida, 1 permitido, NULL motivo, 1 aluno_id
    UNION ALL SELECT DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY) + INTERVAL 68 MINUTE, 1, NULL, 2
    UNION ALL SELECT DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY) + INTERVAL 60 MINUTE, 1, NULL, 3
    UNION ALL SELECT DATE_SUB(NOW(), INTERVAL 5 DAY), NULL, 0, 'Cadastro do aluno esta inativo.', 4
    UNION ALL SELECT DATE_SUB(NOW(), INTERVAL 4 DAY), NULL, 0, 'Mensalidade vencida.', 5
    UNION ALL SELECT DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY) + INTERVAL 55 MINUTE, 1, NULL, 6
    UNION ALL SELECT DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY) + INTERVAL 80 MINUTE, 1, NULL, 7
    UNION ALL SELECT DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY) + INTERVAL 70 MINUTE, 1, NULL, 8
    UNION ALL SELECT NOW(), NULL, 0, 'Mensalidade vencida.', 9
    UNION ALL SELECT NOW(), DATE_ADD(NOW(), INTERVAL 50 MINUTE), 1, NULL, 11
    UNION ALL SELECT DATE_SUB(NOW(), INTERVAL 12 HOUR), DATE_SUB(NOW(), INTERVAL 11 HOUR), 1, NULL, 12
    UNION ALL SELECT DATE_SUB(NOW(), INTERVAL 6 HOUR), DATE_SUB(NOW(), INTERVAL 5 HOUR), 1, NULL, 13
    UNION ALL SELECT DATE_SUB(NOW(), INTERVAL 3 HOUR), DATE_SUB(NOW(), INTERVAL 2 HOUR), 1, NULL, 14
    UNION ALL SELECT DATE_SUB(NOW(), INTERVAL 2 HOUR), NULL, 0, 'Cadastro do aluno esta inativo.', 15
) acessos_seed
WHERE NOT EXISTS (
    SELECT 1 FROM acessos ac
    WHERE ac.Aluno_idAluno = acessos_seed.aluno_id
);
