from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..utils.db import get_connection

planos_bp = Blueprint('planos', __name__)

@planos_bp.route('/', methods=['GET'])
@jwt_required()
def get_all():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM planos ORDER BY nome")
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@planos_bp.route('/', methods=['POST'])
@jwt_required()
def post():
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO planos (nome, valor, duracao) VALUES (%s, %s, %s)",
                (data['nome'], data['valor'], data.get('duracao', 30))
            )
            conn.commit()
            return jsonify({'id': cur.lastrowid, **data}), 201
    finally:
        conn.close()

@planos_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def put(id):
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE planos SET nome=%s, valor=%s, duracao=%s WHERE idPlano=%s",
                (data['nome'], data['valor'], data.get('duracao', 30), id)
            )
            conn.commit()
            return jsonify({'id': id, **data})
    finally:
        conn.close()

@planos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM planos WHERE idPlano = %s", (id,))
            conn.commit()
            return jsonify({'msg': 'Plano removido'})
    finally:
        conn.close()
