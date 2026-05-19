from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..utils.db import get_connection
from ..utils.authz import current_user, is_admin, is_trainer, roles_required
from datetime import datetime

acesso_bp = Blueprint('acesso', __name__)


def validar_acesso(cur, aluno_id):
    cur.execute("SELECT nome, status, Plano_idPlano FROM alunos WHERE idAluno = %s", (aluno_id,))
    aluno = cur.fetchone()
    if not aluno:
        return False, 'Aluno nao encontrado.'
    if aluno['status'] != 'Ativo':
        return False, f"Cadastro do aluno esta {aluno['status'].lower()}."
    if not aluno['Plano_idPlano']:
        return False, 'Aluno sem plano ativo vinculado.'

    cur.execute("""
        SELECT dataVencimento FROM mensalidades
        WHERE Aluno_idAluno = %s AND status = 'Pendente'
        AND dataVencimento < CURDATE()
        ORDER BY dataVencimento ASC
        LIMIT 1
    """, (aluno_id,))
    atraso = cur.fetchone()
    if atraso:
        return False, f"Mensalidade vencida em {atraso['dataVencimento'].strftime('%d/%m/%Y')}."

    return True, 'Acesso liberado.'


@acesso_bp.route('/entrada', methods=['POST'])
@roles_required('admin', 'treinador', 'professor', 'recepcionista')
def registrar_entrada():
    """Valida se aluno pode entrar (mensalidade em dia) e registra acesso."""
    data = request.get_json()
    aluno_id = data.get('aluno_id')

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            permitido, motivo = validar_acesso(cur, aluno_id)

            if not permitido:
                if motivo != 'Aluno nao encontrado.':
                    cur.execute("""
                        INSERT INTO acessos (dataHoraEntrada, Aluno_idAluno, permitido, motivoNegacao)
                        VALUES (%s, %s, %s, %s)
                    """, (datetime.now(), aluno_id, 0, motivo))
                    conn.commit()
                return jsonify({'permitido': False, 'motivo': motivo}), 403

            # Registra entrada
            cur.execute("""
                INSERT INTO acessos (dataHoraEntrada, Aluno_idAluno, permitido)
                VALUES (%s, %s, %s)
            """, (datetime.now(), aluno_id, 1))
            conn.commit()
            return jsonify({'permitido': True, 'motivo': motivo, 'id': cur.lastrowid})
    finally:
        conn.close()

@acesso_bp.route('/status', methods=['GET'])
@jwt_required()
def status_acesso():
    user = current_user()
    aluno_id = request.args.get('aluno_id') or user.get('aluno_id')
    if user['perfil'] == 'aluno' and str(user.get('aluno_id')) != str(aluno_id):
        return jsonify({
            'erro': 'Acesso negado',
            'motivo': 'Alunos podem consultar apenas a propria situacao de acesso.'
        }), 403
    if not (is_admin(user) or is_trainer(user) or user['perfil'] in ('aluno', 'recepcionista')):
        return jsonify({'erro': 'Acesso negado', 'motivo': 'Seu perfil nao pode validar acessos.'}), 403

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            permitido, motivo = validar_acesso(cur, aluno_id)
            return jsonify({'permitido': permitido, 'motivo': motivo})
    finally:
        conn.close()

@acesso_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    user = current_user()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT ac.*, a.nome as aluno_nome
                FROM acessos ac
                JOIN alunos a ON ac.Aluno_idAluno = a.idAluno
            """
            params = ()
            if user['perfil'] == 'aluno':
                sql += " WHERE ac.Aluno_idAluno = %s"
                params = (user.get('aluno_id'),)
            elif not (is_admin(user) or is_trainer(user) or user['perfil'] == 'recepcionista'):
                return jsonify({'erro': 'Acesso negado', 'motivo': 'Seu perfil nao pode consultar acessos.'}), 403
            sql += " ORDER BY ac.dataHoraEntrada DESC LIMIT 50"
            cur.execute(sql, params)
            return jsonify(cur.fetchall())
    finally:
        conn.close()
