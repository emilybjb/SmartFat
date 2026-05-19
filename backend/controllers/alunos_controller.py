from ..utils.db import get_connection


def only_digits(value):
    return ''.join(char for char in str(value or '') if char.isdigit())


def listar_alunos():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT a.*, p.nome as plano_nome
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
            cur.execute("""
                INSERT INTO alunos (nome, CPF, telefone, status, Plano_idPlano)
                VALUES (%s, %s, %s, %s, %s)
            """, (data['nome'], cpf, telefone or None, 'Ativo', data.get('Plano_idPlano')))
            conn.commit()
            return {'id': cur.lastrowid, **data}
    finally:
        conn.close()

def atualizar_aluno(id, data):
    telefone = only_digits(data.get('telefone'))
    if telefone and len(telefone) > 11:
        raise ValueError('Telefone deve conter no maximo 11 digitos.')

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE alunos SET nome=%s, telefone=%s, status=%s, Plano_idPlano=%s
                WHERE idAluno=%s
            """, (data['nome'], telefone or None, data.get('status', 'Ativo'), data.get('Plano_idPlano'), id))
            conn.commit()
            return {'id': id, **data}
    finally:
        conn.close()

def deletar_aluno(id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM alunos WHERE idAluno = %s", (id,))
            conn.commit()
    finally:
        conn.close()
