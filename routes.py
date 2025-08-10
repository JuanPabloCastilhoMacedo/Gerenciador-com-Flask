from flask import Blueprint, request, jsonify, url_for
from models import db, User
import bcrypt, uuid

bp = Blueprint('routes', __name__)

@bp.route('/register', methods=['POST'])
def register():
    dados = request.json
    email = dados.get("email")
    senha = dados.get("senha")

    if not email or not senha:
        return jsonify({"Status": "ERRO", "mensagem": "Email e senha são obrigatórios"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"Status": "ERRO", "mensagem": "Email já cadastrado"}), 409

    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    novo_usuario = User(email=email, senha_hash=senha_hash)
    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({"Status": "OK", "mensagem": "Usuário registrado com sucesso"})

@bp.route('/login', methods=['POST'])
def login():
    dados = request.json
    email = dados.get("email")
    senha = dados.get("senha")

    usuario = User.query.filter_by(email=email).first()
    if usuario and bcrypt.checkpw(senha.encode(), usuario.senha_hash.encode()):
        return jsonify({"Status": "OK", "mensagem": "Login realizado"})
    else:
        return jsonify({"Status": "ERRO", "mensagem": "Credenciais inválidas"})
    
#POST /forgot-password — receba o email, gere um token e salve no bancoS
@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json.get("email")
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"Status": "ERRO", "mensagem": "Email não encontrado"}), 404
    token = str(uuid.uuid4())
    user.reset_token = token
    db.session.commit()
    reset_url = url_for('routes.reset_password', token=token, _external=True)
    # Aqui você enviaria o reset_url por email.
    return jsonify({"Status": "OK", "mensagem": f"Link de recuperação: {reset_url}"})

#POST /reset-password/<token> — receba a nova senha via JSON e atualize o usuário
@bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return jsonify({"Status": "ERRO", "mensagem": "Token inválido"}), 400
    nova_senha = request.json.get("senha")
    if not nova_senha:
        return jsonify({"Status": "ERRO", "mensagem": "Senha obrigatória"}), 400
    user.senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
    user.reset_token = None
    db.session.commit()
    return jsonify({"Status": "OK", "mensagem": "Senha redefinida com sucesso"})
