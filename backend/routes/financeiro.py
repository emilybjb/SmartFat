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
            cur.execute("""
                SELECT COALESCE(SUM(m.valor), 0) as total_recebido
                FROM mensalidades m
                WHERE m.status='Pago'
            """)
            recebido = cur.fetchone()
            cur.execute("SELECT COALESCE(SUM(valor), 0) as total_pendente FROM mensalidades WHERE status='Pendente'")
            pendente = cur.fetchone()
            cur.execute("SELECT COUNT(*) as total_alunos FROM alunos WHERE status='Ativo'")
            alunos = cur.fetchone()
            cur.execute("""
                SELECT COUNT(*) as mensalidades_vencidas
                FROM mensalidades
                WHERE status='Pendente' AND dataVencimento < CURDATE()
            """)
            vencidas = cur.fetchone()
        return jsonify({
            'total_recebido': recebido['total_recebido'] or 0,
            'total_pendente': pendente['total_pendente'] or 0,
            'total_alunos_ativos': alunos['total_alunos'],
            'mensalidades_vencidas': vencidas['mensalidades_vencidas']
        })
    finally:
        conn.close()
