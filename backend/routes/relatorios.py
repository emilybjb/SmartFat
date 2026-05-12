from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ..utils.db import get_connection

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/financeiro', methods=['GET'])
@jwt_required()
def relatorio_financeiro():
    """Relatório financeiro por período."""
    periodo = request.args.get('periodo', 1)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT periodo, totalReceita FROM relatorios_financeiros
                ORDER BY periodo DESC LIMIT %s
            """, (int(periodo),))
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@relatorios_bp.route('/operacional', methods=['GET'])
@jwt_required()
def relatorio_operacional():
    """Relatório operacional: frequência e acessos."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ro.*, a.nome as aluno_nome
                FROM relatorios_operacionais ro
                JOIN alunos a ON ro.Aluno_idAluno = a.idAluno
                ORDER BY ro.frequenciaMensal DESC
            """)
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@relatorios_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """Dados consolidados para o dashboard."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total FROM alunos WHERE status='Ativo'")
            alunos_ativos = cur.fetchone()['total']

            cur.execute("SELECT COUNT(*) as total FROM mensalidades WHERE status='Pendente'")
            mensalidades_pendentes = cur.fetchone()['total']

            cur.execute("SELECT COALESCE(SUM(valor),0) as total FROM mensalidades WHERE status='Pago' AND MONTH(dataVencimento)=MONTH(CURDATE())")
            receita_mes = cur.fetchone()['total']

            cur.execute("SELECT COUNT(*) as total FROM acessos WHERE DATE(dataHoraEntrada)=CURDATE()")
            acessos_hoje = cur.fetchone()['total']

        return jsonify({
            'alunos_ativos': alunos_ativos,
            'mensalidades_pendentes': mensalidades_pendentes,
            'receita_mes': float(receita_mes),
            'acessos_hoje': acessos_hoje
        })
    finally:
        conn.close()
