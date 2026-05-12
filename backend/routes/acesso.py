from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..utils.db import get_connection
from datetime import datetime

acesso_bp = Blueprint('acesso', __name__)

@acesso_bp.route('/entrada', methods=['POST'])
@jwt_required()
def registrar_entrada():
    """Valida se aluno pode entrar (mensalidade em dia) e registra acesso."""
    data = request.get_json()
    aluno_id = data.get('aluno_id')

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Valida situação financeira (módulo ValidacaoAcesso)
            cur.execute("""
                SELECT COUNT(*) as pendentes FROM mensalidades
                WHERE Aluno_idAluno = %s AND status = 'Pendente'
                AND dataVencimento < CURDATE()
            """, (aluno_id,))
            pendentes = cur.fetchone()['pendentes']

            if pendentes > 0:
                return jsonify({'permitido': False, 'motivo': 'Mensalidade em atraso'}), 403

            # Registra entrada
            cur.execute("""
                INSERT INTO acessos (dataHoraEntrada, Aluno_idAluno)
                VALUES (%s, %s)
            """, (datetime.now(), aluno_id))
            conn.commit()
            return jsonify({'permitido': True, 'id': cur.lastrowid})
    finally:
        conn.close()

@acesso_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ac.*, a.nome as aluno_nome
                FROM acessos ac
                JOIN alunos a ON ac.Aluno_idAluno = a.idAluno
                ORDER BY ac.dataHoraEntrada DESC LIMIT 50
            """)
            return jsonify(cur.fetchall())
    finally:
        conn.close()
