from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..utils.db import get_connection
from ..utils.authz import roles_required
from ..controllers.alunos_controller import ensure_unique_cpf, only_digits
import bcrypt

auth_bp = Blueprint('auth', __name__)


def validar_acesso_aluno(cur, aluno_id):
    if not aluno_id:
        return {'permitido': False, 'motivo': 'Usuario de aluno sem cadastro vinculado.'}

    cur.execute("SELECT nome, status, Plano_idPlano FROM alunos WHERE idAluno = %s", (aluno_id,))
    aluno = cur.fetchone()
    if not aluno:
        return {'permitido': False, 'motivo': 'Aluno nao encontrado no cadastro.'}
    if aluno['status'] != 'Ativo':
        return {'permitido': False, 'motivo': f"Cadastro do aluno esta {aluno['status'].lower()}."}
    if not aluno['Plano_idPlano']:
        return {'permitido': False, 'motivo': 'Aluno sem plano ativo vinculado.'}

    cur.execute("""
        SELECT dataVencimento FROM mensalidades
        WHERE Aluno_idAluno = %s AND status = 'Pendente'
        AND dataVencimento < CURDATE()
        ORDER BY dataVencimento ASC
        LIMIT 1
    """, (aluno_id,))
    atraso = cur.fetchone()
    if atraso:
        return {
            'permitido': False,
            'motivo': f"Mensalidade vencida em {atraso['dataVencimento'].strftime('%d/%m/%Y')}."
        }

    return {'permitido': True, 'motivo': 'Acesso liberado.'}

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
            aviso_acesso = None
            if usuario and usuario['perfil'] == 'aluno':
                aviso_acesso = validar_acesso_aluno(cur, usuario.get('Aluno_idAluno'))
    finally:
        conn.close()

    if not usuario or not bcrypt.checkpw(senha.encode(), usuario['senha'].encode()):
        return jsonify({'erro': 'Credenciais inválidas'}), 401

    token = create_access_token(
        identity=str(usuario['id']),
        additional_claims={
            'perfil': usuario['perfil'],
            'aluno_id': usuario.get('Aluno_idAluno')
        }
    )
    return jsonify({
        'token': token,
        'perfil': usuario['perfil'],
        'nome': usuario['nome'],
        'aluno_id': usuario.get('Aluno_idAluno'),
        'aviso_acesso': aviso_acesso
    })


def hash_senha(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt(rounds=12)).decode()


@auth_bp.route('/cadastro', methods=['POST'])
@roles_required('admin')
def cadastrar_usuario():
    data = request.get_json()
    tipo = data.get('tipo')
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({'erro': 'Nome, e-mail e senha sao obrigatorios.'}), 400

    if tipo not in ('aluno', 'professor'):
        return jsonify({'erro': 'Tipo de cadastro invalido.'}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cur.fetchone():
                return jsonify({'erro': 'Ja existe um usuario com este e-mail.'}), 409

            senha_hash = hash_senha(senha)

            if tipo == 'professor':
                perfil = data.get('perfil') or 'treinador'
                if perfil not in ('treinador', 'professor'):
                    return jsonify({'erro': 'Perfil de professor invalido.'}), 400

                cur.execute("""
                    INSERT INTO usuarios (nome, email, senha, perfil)
                    VALUES (%s, %s, %s, %s)
                """, (nome, email, senha_hash, perfil))
                conn.commit()
                return jsonify({
                    'msg': 'Professor cadastrado com sucesso.',
                    'usuario_id': cur.lastrowid,
                    'perfil': perfil
                }), 201

            cpf = only_digits(data.get('CPF'))
            telefone = only_digits(data.get('telefone'))
            plano_id = data.get('Plano_idPlano')
            vencimento = data.get('dataVencimento')
            if not cpf or not plano_id or not vencimento:
                return jsonify({'erro': 'CPF, plano e vencimento inicial sao obrigatorios para cadastrar aluno.'}), 400
            if len(cpf) != 11:
                return jsonify({'erro': 'CPF deve conter exatamente 11 digitos.'}), 400
            if telefone and len(telefone) > 11:
                return jsonify({'erro': 'Telefone deve conter no maximo 11 digitos.'}), 400

            try:
                ensure_unique_cpf(cur, cpf)
            except ValueError as error:
                return jsonify({'erro': str(error)}), 409

            cur.execute("SELECT valor FROM planos WHERE idPlano = %s", (plano_id,))
            plano = cur.fetchone()
            if not plano:
                return jsonify({'erro': 'Plano informado nao existe.'}), 400

            cur.execute("""
                INSERT INTO alunos (nome, CPF, telefone, status, Plano_idPlano)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                nome,
                cpf,
                telefone or None,
                data.get('status') or 'Ativo',
                plano_id
            ))
            aluno_id = cur.lastrowid

            cur.execute("""
                INSERT INTO usuarios (nome, email, senha, perfil, Aluno_idAluno)
                VALUES (%s, %s, %s, 'aluno', %s)
            """, (nome, email, senha_hash, aluno_id))

            cur.execute("""
                INSERT INTO mensalidades (valor, dataVencimento, status, Aluno_idAluno, Financeiro_idFinanceiro)
                VALUES (%s, %s, 'Pendente', %s, %s)
            """, (
                plano['valor'],
                vencimento,
                aluno_id,
                data.get('Financeiro_idFinanceiro')
            ))

            conn.commit()
            return jsonify({
                'msg': 'Aluno cadastrado com login e mensalidade inicial.',
                'aluno_id': aluno_id
            }), 201
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
