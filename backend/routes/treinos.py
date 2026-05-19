from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..utils.db import get_connection
from ..utils.authz import current_user, is_admin, is_trainer, roles_required

treinos_bp = Blueprint('treinos', __name__)

@treinos_bp.route('/', methods=['GET'])
@jwt_required()
def get_treinos():
    user = current_user()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT t.*, a.nome as aluno_nome
                FROM treinos t
                JOIN alunos a ON t.Aluno_idTreino = a.idAluno
            """
            params = ()
            if user['perfil'] == 'aluno':
                sql += " WHERE t.Aluno_idTreino = %s"
                params = (user.get('aluno_id'),)
            elif not (is_admin(user) or is_trainer(user)):
                return jsonify({'erro': 'Acesso negado', 'motivo': 'Seu perfil nao pode consultar treinos.'}), 403
            sql += " ORDER BY t.data DESC"
            cur.execute(sql, params)
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@treinos_bp.route('/', methods=['POST'])
@roles_required('admin', 'treinador', 'professor')
def criar_treino():
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO treinos (descricao, data, Aluno_idTreino) VALUES (%s, %s, %s)",
                (data['descricao'], data['data'], data['Aluno_idTreino'])
            )
            conn.commit()
            return jsonify({'id': cur.lastrowid}), 201
    finally:
        conn.close()

@treinos_bp.route('/<int:id>', methods=['PUT'])
@roles_required('admin', 'treinador', 'professor')
def atualizar_treino(id):
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE treinos
                SET descricao=%s, data=%s, Aluno_idTreino=%s
                WHERE idTreino=%s
            """, (data['descricao'], data['data'], data['Aluno_idTreino'], id))
            conn.commit()
            return jsonify({'msg': 'Treino atualizado'})
    finally:
        conn.close()

@treinos_bp.route('/<int:id>', methods=['DELETE'])
@roles_required('admin', 'treinador', 'professor')
def remover_treino(id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM treinos WHERE idTreino=%s", (id,))
            conn.commit()
            return jsonify({'msg': 'Treino removido'})
    finally:
        conn.close()

@treinos_bp.route('/avaliacoes', methods=['GET'])
@jwt_required()
def get_avaliacoes():
    user = current_user()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT av.*, a.nome as aluno_nome
                FROM avaliacoes_fisicas av
                JOIN alunos a ON av.Aluno_idAluno = a.idAluno
            """
            params = ()
            if user['perfil'] == 'aluno':
                sql += " WHERE av.Aluno_idAluno = %s"
                params = (user.get('aluno_id'),)
            elif not (is_admin(user) or is_trainer(user)):
                return jsonify({'erro': 'Acesso negado', 'motivo': 'Seu perfil nao pode consultar avaliacoes.'}), 403
            sql += " ORDER BY av.idAvaliacaoFisica DESC"
            cur.execute(sql, params)
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@treinos_bp.route('/avaliacoes', methods=['POST'])
@roles_required('admin', 'treinador', 'professor')
def criar_avaliacao():
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO avaliacoes_fisicas (peso, altura, Aluno_idAluno) VALUES (%s, %s, %s)",
                (data['peso'], data['altura'], data['Aluno_idAluno'])
            )
            conn.commit()
            return jsonify({'id': cur.lastrowid}), 201
    finally:
        conn.close()

@treinos_bp.route('/avaliacoes/<int:id>', methods=['PUT'])
@roles_required('admin', 'treinador', 'professor')
def atualizar_avaliacao(id):
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE avaliacoes_fisicas
                SET peso=%s, altura=%s, Aluno_idAluno=%s
                WHERE idAvaliacaoFisica=%s
            """, (data['peso'], data['altura'], data['Aluno_idAluno'], id))
            conn.commit()
            return jsonify({'msg': 'Avaliacao atualizada'})
    finally:
        conn.close()

@treinos_bp.route('/avaliacoes/<int:id>', methods=['DELETE'])
@roles_required('admin', 'treinador', 'professor')
def remover_avaliacao(id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM avaliacoes_fisicas WHERE idAvaliacaoFisica=%s", (id,))
            conn.commit()
            return jsonify({'msg': 'Avaliacao removida'})
    finally:
        conn.close()
