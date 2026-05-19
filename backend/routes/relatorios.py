from flask import Blueprint, jsonify, request
from ..utils.db import get_connection
from ..utils.authz import roles_required

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/financeiro', methods=['GET'])
@roles_required('admin')
def relatorio_financeiro():
    """Relatório financeiro agrupado por mês."""
    meses = int(request.args.get('meses', 6))
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    DATE_FORMAT(dataVencimento, '%%Y-%%m') as periodo,
                    COALESCE(SUM(CASE WHEN status = 'Pago' THEN valor ELSE 0 END), 0) as recebido,
                    COALESCE(SUM(CASE WHEN status = 'Pendente' THEN valor ELSE 0 END), 0) as pendente,
                    COUNT(*) as total_mensalidades
                FROM mensalidades
                GROUP BY DATE_FORMAT(dataVencimento, '%%Y-%%m')
                ORDER BY periodo DESC
                LIMIT %s
            """, (meses,))
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@relatorios_bp.route('/operacional', methods=['GET'])
@roles_required('admin')
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

@relatorios_bp.route('/acesso', methods=['GET'])
@roles_required('admin')
def relatorio_acesso():
    """Relatório de liberações e bloqueios de acesso por aluno."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    a.nome as aluno_nome,
                    COUNT(ac.idAcesso) as total_tentativas,
                    SUM(CASE WHEN ac.permitido = 1 THEN 1 ELSE 0 END) as liberados,
                    SUM(CASE WHEN ac.permitido = 0 THEN 1 ELSE 0 END) as negados,
                    MAX(ac.dataHoraEntrada) as ultimo_acesso,
                    SUBSTRING_INDEX(
                        GROUP_CONCAT(ac.motivoNegacao ORDER BY ac.dataHoraEntrada DESC SEPARATOR '||'),
                        '||',
                        1
                    ) as ultimo_motivo_negado
                FROM acessos ac
                JOIN alunos a ON ac.Aluno_idAluno = a.idAluno
                GROUP BY a.idAluno, a.nome
                ORDER BY ultimo_acesso DESC
            """)
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@relatorios_bp.route('/dashboard', methods=['GET'])
@roles_required('admin')
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
