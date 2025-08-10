from flask import Blueprint, request, jsonify
from models import db, User
import bcrypt

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