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


def atualizar_relatorio_operacional(cur, aluno_id):
    cur.execute("""
        SELECT
            COUNT(*) as frequencia_mensal,
            COALESCE(SUM(TIMESTAMPDIFF(MINUTE, dataHoraEntrada, dataHoraSaida)), 0) as minutos_treino
        FROM acessos
        WHERE Aluno_idAluno = %s
          AND permitido = 1
          AND MONTH(dataHoraEntrada) = MONTH(CURDATE())
          AND YEAR(dataHoraEntrada) = YEAR(CURDATE())
    """, (aluno_id,))
    dados = cur.fetchone()
    frequencia = dados['frequencia_mensal'] or 0
    aulas = max(1, int((dados['minutos_treino'] or 0) / 45)) if frequencia else 0

    cur.execute("""
        SELECT idRelatorioOperacional
        FROM relatorios_operacionais
        WHERE Aluno_idAluno = %s
        ORDER BY idRelatorioOperacional DESC
        LIMIT 1
    """, (aluno_id,))
    relatorio = cur.fetchone()

    if relatorio:
        relatorio_id = relatorio['idRelatorioOperacional']
        cur.execute("""
            UPDATE relatorios_operacionais
            SET frequenciaMensal=%s, quantAulas=%s
            WHERE idRelatorioOperacional=%s
        """, (frequencia, aulas, relatorio_id))
        return relatorio_id

    cur.execute("""
        INSERT INTO relatorios_operacionais (frequenciaMensal, quantAulas, Aluno_idAluno)
        VALUES (%s, %s, %s)
    """, (frequencia, aulas, aluno_id))
    return cur.lastrowid


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
            acesso_id = cur.lastrowid
            relatorio_id = atualizar_relatorio_operacional(cur, aluno_id)
            cur.execute("""
                UPDATE acessos
                SET RelatorioOperacional_idRelatorioOperacional=%s
                WHERE idAcesso=%s
            """, (relatorio_id, acesso_id))
            conn.commit()
            return jsonify({'permitido': True, 'motivo': motivo, 'id': acesso_id})
    finally:
        conn.close()

@acesso_bp.route('/saida', methods=['PUT'])
@roles_required('admin', 'treinador', 'professor', 'recepcionista')
def registrar_saida():
    data = request.get_json()
    aluno_id = data.get('aluno_id')

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT idAcesso
                FROM acessos
                WHERE Aluno_idAluno=%s
                  AND permitido=1
                  AND dataHoraSaida IS NULL
                ORDER BY dataHoraEntrada DESC
                LIMIT 1
            """, (aluno_id,))
            acesso = cur.fetchone()
            if not acesso:
                return jsonify({'erro': 'Nao existe entrada aberta para este aluno.'}), 404

            cur.execute("""
                UPDATE acessos
                SET dataHoraSaida=%s
                WHERE idAcesso=%s
            """, (datetime.now(), acesso['idAcesso']))
            relatorio_id = atualizar_relatorio_operacional(cur, aluno_id)
            cur.execute("""
                UPDATE acessos
                SET RelatorioOperacional_idRelatorioOperacional=%s
                WHERE idAcesso=%s
            """, (relatorio_id, acesso['idAcesso']))
            conn.commit()
            return jsonify({'msg': 'Saida registrada', 'id': acesso['idAcesso']})
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
