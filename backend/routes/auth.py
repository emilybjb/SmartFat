from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..utils.db import get_connection
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            usuario = cur.fetchone()
    finally:
        conn.close()

    if not usuario or not bcrypt.checkpw(senha.encode(), usuario['senha'].encode()):
        return jsonify({'erro': 'Credenciais inválidas'}), 401

    token = create_access_token(
        identity=str(usuario['id']),
        additional_claims={'perfil': usuario['perfil']}
    )
    return jsonify({'token': token, 'perfil': usuario['perfil'], 'nome': usuario['nome']})
