from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..utils.db import get_connection

mensalidades_bp = Blueprint('mensalidades', __name__)

@mensalidades_bp.route('/', methods=['GET'])
@jwt_required()
def get_all():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT m.*, a.nome as aluno_nome
                FROM mensalidades m
                JOIN alunos a ON m.Aluno_idAluno = a.idAluno
                ORDER BY m.dataVencimento DESC
            """)
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@mensalidades_bp.route('/', methods=['POST'])
@jwt_required()
def post():
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO mensalidades (valor, dataVencimento, status, Aluno_idAluno, Financeiro_idFinanceiro)
                VALUES (%s, %s, %s, %s, %s)
            """, (data['valor'], data['dataVencimento'], 'Pendente', data['Aluno_idAluno'], data.get('Financeiro_idFinanceiro')))
            conn.commit()
            return jsonify({'id': cur.lastrowid}), 201
    finally:
        conn.close()

@mensalidades_bp.route('/<int:id>/pagar', methods=['PUT'])
@jwt_required()
def pagar(id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE mensalidades SET status='Pago' WHERE idMensalidade=%s", (id,))
            conn.commit()
            return jsonify({'msg': 'Mensalidade paga'})
    finally:
        conn.close()
