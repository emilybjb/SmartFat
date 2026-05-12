from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..controllers.alunos_controller import (
    listar_alunos, buscar_aluno, criar_aluno, atualizar_aluno, deletar_aluno
)

alunos_bp = Blueprint('alunos', __name__)

@alunos_bp.route('/', methods=['GET'])
@jwt_required()
def get_all():
    return jsonify(listar_alunos())

@alunos_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_one(id):
    aluno = buscar_aluno(id)
    if not aluno:
        return jsonify({'erro': 'Aluno não encontrado'}), 404
    return jsonify(aluno)

@alunos_bp.route('/', methods=['POST'])
@jwt_required()
def post():
    return jsonify(criar_aluno(request.get_json())), 201

@alunos_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def put(id):
    return jsonify(atualizar_aluno(id, request.get_json()))

@alunos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    deletar_aluno(id)
    return jsonify({'msg': 'Aluno removido'})
