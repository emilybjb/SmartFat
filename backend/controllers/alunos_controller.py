from ..utils.db import get_connection


def only_digits(value):
    return ''.join(char for char in str(value or '') if char.isdigit())


def cpf_filter_sql(column='CPF'):
    return f"REPLACE(REPLACE({column}, '.', ''), '-', '')"


def ensure_unique_cpf(cur, cpf, ignored_id=None):
    params = [cpf]
    sql = f"SELECT idAluno FROM alunos WHERE {cpf_filter_sql()} = %s"
    if ignored_id:
        sql += " AND idAluno <> %s"
        params.append(ignored_id)
    cur.execute(sql, tuple(params))
    if cur.fetchone():
        raise ValueError('Ja existe um aluno com este CPF.')


def listar_alunos():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT a.*, p.nome as plano_nome, p.valor as plano_valor
                FROM alunos a
                LEFT JOIN planos p ON a.Plano_idPlano = p.idPlano
                ORDER BY a.nome
            """)
            return cur.fetchall()
    finally:
        conn.close()

def buscar_aluno(id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM alunos WHERE idAluno = %s", (id,))
            return cur.fetchone()
    finally:
        conn.close()

def criar_aluno(data):
    cpf = only_digits(data.get('CPF'))
    telefone = only_digits(data.get('telefone'))
    if len(cpf) != 11:
        raise ValueError('CPF deve conter exatamente 11 digitos.')
    if telefone and len(telefone) > 11:
        raise ValueError('Telefone deve conter no maximo 11 digitos.')

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            ensure_unique_cpf(cur, cpf)
            cur.execute("""
                INSERT INTO alunos (nome, CPF, telefone, status, Plano_idPlano)
                VALUES (%s, %s, %s, %s, %s)
            """, (data['nome'], cpf, telefone or None, 'Ativo', data.get('Plano_idPlano')))
            conn.commit()
            return {'id': cur.lastrowid, **data}
    finally:
        conn.close()

def atualizar_aluno(id, data):
    cpf = only_digits(data.get('CPF'))
    telefone = only_digits(data.get('telefone'))
    if cpf and len(cpf) != 11:
        raise ValueError('CPF deve conter exatamente 11 digitos.')
    if telefone and len(telefone) > 11:
        raise ValueError('Telefone deve conter no maximo 11 digitos.')

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT CPF FROM alunos WHERE idAluno = %s", (id,))
            aluno = cur.fetchone()
            if not aluno:
                raise ValueError('Aluno nao encontrado.')

            cpf_final = cpf or only_digits(aluno.get('CPF'))
            ensure_unique_cpf(cur, cpf_final, id)
            cur.execute("""
                UPDATE alunos SET nome=%s, CPF=%s, telefone=%s, status=%s, Plano_idPlano=%s
                WHERE idAluno=%s
            """, (data['nome'], cpf_final, telefone or None, data.get('status', 'Ativo'), data.get('Plano_idPlano'), id))
            conn.commit()
            return {'id': id, **data}
    finally:
        conn.close()

def deletar_aluno(id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT idAluno FROM alunos WHERE idAluno = %s", (id,))
            if not cur.fetchone():
                raise ValueError('Aluno nao encontrado.')

            cur.execute("UPDATE usuarios SET Aluno_idAluno = NULL WHERE Aluno_idAluno = %s", (id,))
            cur.execute("DELETE FROM acessos WHERE Aluno_idAluno = %s", (id,))
            cur.execute("DELETE FROM relatorios_operacionais WHERE Aluno_idAluno = %s", (id,))
            cur.execute("DELETE FROM mensalidades WHERE Aluno_idAluno = %s", (id,))
            cur.execute("DELETE FROM treinos WHERE Aluno_idTreino = %s", (id,))
            cur.execute("DELETE FROM avaliacoes_fisicas WHERE Aluno_idAluno = %s", (id,))
            cur.execute("DELETE FROM alunos WHERE idAluno = %s", (id,))
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
