from flask import Blueprint, jsonify
from ..utils.db import get_connection
from ..utils.authz import roles_required

financeiro_bp = Blueprint('financeiro', __name__)

@financeiro_bp.route('/resumo', methods=['GET'])
@roles_required('admin')
def resumo():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT SUM(valor) as total_recebido FROM mensalidades WHERE status='Pago'")
            recebido = cur.fetchone()
            cur.execute("SELECT SUM(valor) as total_pendente FROM mensalidades WHERE status='Pendente'")
            pendente = cur.fetchone()
            cur.execute("SELECT COUNT(*) as total_alunos FROM alunos WHERE status='Ativo'")
            alunos = cur.fetchone()
        return jsonify({
            'total_recebido': recebido['total_recebido'] or 0,
            'total_pendente': pendente['total_pendente'] or 0,
            'total_alunos_ativos': alunos['total_alunos']
        })
    finally:
        conn.close()
