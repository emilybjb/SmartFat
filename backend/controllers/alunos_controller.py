from ..utils.db import get_connection

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
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO alunos (nome, CPF, telefone, status, Plano_idPlano)
                VALUES (%s, %s, %s, %s, %s)
            """, (data['nome'], data['CPF'], data.get('telefone'), 'Ativo', data.get('Plano_idPlano')))
            conn.commit()
            return {'id': cur.lastrowid, **data}
    finally:
        conn.close()

def atualizar_aluno(id, data):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE alunos SET nome=%s, telefone=%s, status=%s, Plano_idPlano=%s
                WHERE idAluno=%s
            """, (data['nome'], data.get('telefone'), data.get('status', 'Ativo'), data.get('Plano_idPlano'), id))
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
