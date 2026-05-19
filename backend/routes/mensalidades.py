from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..utils.db import get_connection
from ..utils.authz import current_user, is_admin, roles_required

mensalidades_bp = Blueprint('mensalidades', __name__)

@mensalidades_bp.route('/', methods=['GET'])
@jwt_required()
def get_all():
    user = current_user()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT m.*, a.nome as aluno_nome, f.dataPagamento
                FROM mensalidades m
                JOIN alunos a ON m.Aluno_idAluno = a.idAluno
                LEFT JOIN financeiros f ON m.Financeiro_idFinanceiro = f.idFinanceiro
            """
            params = ()
            if user['perfil'] == 'aluno':
                sql += " WHERE m.Aluno_idAluno = %s"
                params = (user.get('aluno_id'),)
            elif not is_admin(user):
                return jsonify({
                    'erro': 'Acesso negado',
                    'motivo': 'Somente administradores e o proprio aluno podem consultar mensalidades.'
                }), 403
            sql += " ORDER BY m.dataVencimento DESC"
            cur.execute(sql, params)
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@mensalidades_bp.route('/', methods=['POST'])
@roles_required('admin')
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
    user = current_user()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT idMensalidade, valor, status, Aluno_idAluno, Financeiro_idFinanceiro
                FROM mensalidades
                WHERE idMensalidade=%s
            """, (id,))
            mensalidade = cur.fetchone()
            if not mensalidade:
                return jsonify({'erro': 'Mensalidade nao encontrada.'}), 404

            if user['perfil'] == 'aluno':
                if not mensalidade or int(mensalidade['Aluno_idAluno']) != int(user.get('aluno_id') or 0):
                    return jsonify({
                        'erro': 'Acesso negado',
                        'motivo': 'Alunos podem pagar apenas as proprias mensalidades.'
                    }), 403
            elif not is_admin(user):
                return jsonify({
                    'erro': 'Acesso negado',
                    'motivo': 'Somente administradores e o proprio aluno podem marcar mensalidades como pagas.'
                }), 403

            if mensalidade['status'] == 'Pago':
                return jsonify({'msg': 'Mensalidade ja estava paga'})

            cur.execute("""
                INSERT INTO financeiros (valor, dataPagamento)
                VALUES (%s, CURDATE())
            """, (mensalidade['valor'],))
            financeiro_id = cur.lastrowid

            cur.execute("""
                UPDATE mensalidades
                SET status='Pago', Financeiro_idFinanceiro=%s
                WHERE idMensalidade=%s
            """, (financeiro_id, id))
            conn.commit()
            return jsonify({'msg': 'Mensalidade paga', 'financeiro_id': financeiro_id})
    finally:
        conn.close()
