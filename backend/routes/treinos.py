from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..utils.db import get_connection

treinos_bp = Blueprint('treinos', __name__)

@treinos_bp.route('/', methods=['GET'])
@jwt_required()
def get_treinos():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.*, a.nome as aluno_nome
                FROM treinos t
                JOIN alunos a ON t.Aluno_idTreino = a.idAluno
                ORDER BY t.data DESC
            """)
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@treinos_bp.route('/', methods=['POST'])
@jwt_required()
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

@treinos_bp.route('/avaliacoes', methods=['GET'])
@jwt_required()
def get_avaliacoes():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT av.*, a.nome as aluno_nome
                FROM avaliacoes_fisicas av
                JOIN alunos a ON av.Aluno_idAluno = a.idAluno
                ORDER BY av.idAvaliacaoFisica DESC
            """)
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@treinos_bp.route('/avaliacoes', methods=['POST'])
@jwt_required()
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
