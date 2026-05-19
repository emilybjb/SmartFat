from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required


ROLE_LABELS = {
    'admin': 'administrador',
    'aluno': 'aluno',
    'treinador': 'treinador',
    'professor': 'professor',
    'recepcionista': 'recepcionista',
}


def current_user():
    claims = get_jwt()
    return {
        'id': int(get_jwt_identity()),
        'perfil': claims.get('perfil', 'recepcionista'),
        'aluno_id': claims.get('aluno_id'),
    }


def profile_name(perfil):
    return ROLE_LABELS.get(perfil, perfil or 'usuario')


def permission_denied(required):
    readable = ', '.join(profile_name(role) for role in required)
    return jsonify({
        'erro': 'Acesso negado',
        'motivo': f'Esta area exige perfil de {readable}. Seu usuario nao tem essa permissao.'
    }), 403


def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = current_user()
            if user['perfil'] not in roles:
                return permission_denied(roles)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def is_admin(user=None):
    user = user or current_user()
    return user['perfil'] == 'admin'


def is_trainer(user=None):
    user = user or current_user()
    return user['perfil'] in ('treinador', 'professor')


def is_student(user=None):
    user = user or current_user()
    return user['perfil'] == 'aluno'
