from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..utils.authz import current_user, is_admin, is_trainer, roles_required
from ..controllers.alunos_controller import (
    listar_alunos, buscar_aluno, criar_aluno, atualizar_aluno, deletar_aluno
)

alunos_bp = Blueprint('alunos', __name__)

@alunos_bp.route('/', methods=['GET'])
@jwt_required()
def get_all():
    user = current_user()
    if not (is_admin(user) or is_trainer(user)):
        return jsonify({
            'erro': 'Acesso negado',
            'motivo': 'Somente administradores e treinadores podem consultar a lista de alunos.'
        }), 403
    return jsonify(listar_alunos())

@alunos_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_one(id):
    user = current_user()
    if user['perfil'] == 'aluno' and int(user.get('aluno_id') or 0) != id:
        return jsonify({
            'erro': 'Acesso negado',
            'motivo': 'Alunos podem consultar apenas o proprio cadastro.'
        }), 403
    if not (is_admin(user) or is_trainer(user) or user['perfil'] == 'aluno'):
        return jsonify({
            'erro': 'Acesso negado',
            'motivo': 'Seu perfil nao pode consultar cadastro de alunos.'
        }), 403
    aluno = buscar_aluno(id)
    if not aluno:
        return jsonify({'erro': 'Aluno não encontrado'}), 404
    return jsonify(aluno)

@alunos_bp.route('/', methods=['POST'])
@roles_required('admin')
def post():
    try:
        return jsonify(criar_aluno(request.get_json())), 201
    except ValueError as error:
        return jsonify({'erro': str(error)}), 400

@alunos_bp.route('/<int:id>', methods=['PUT'])
@roles_required('admin')
def put(id):
    try:
        return jsonify(atualizar_aluno(id, request.get_json()))
    except ValueError as error:
        return jsonify({'erro': str(error)}), 400

@alunos_bp.route('/<int:id>', methods=['DELETE'])
@roles_required('admin')
def delete(id):
    deletar_aluno(id)
    return jsonify({'msg': 'Aluno removido'})
