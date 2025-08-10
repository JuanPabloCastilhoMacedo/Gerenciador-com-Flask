from flask import Blueprint, request, jsonify, current_app
from models import db, User, PasswordResetToken
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import sendgrid
from sendgrid.helpers.mail import Mail
import os
import uuid

routes = Blueprint("routes", __name__)

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://gerenciador-com-flask.onrender.com")
MAIL_SENDER = os.getenv("MAIL_SENDER", "701juanpablo2016@gmail.com")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

@routes.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    senha = data.get("senha")

    if not email or not senha:
        return jsonify({"error": "E-mail e senha são obrigatórios"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Usuário já existe"}), 400

    senha_hash = generate_password_hash(senha)
    user = User(email=email, senha_hash=senha_hash)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Usuário registrado com sucesso"}), 201

@routes.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    senha = data.get("senha")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.senha_hash, senha):
        return jsonify({"error": "Credenciais inválidas"}), 401

    return jsonify({"message": "Login bem-sucedido"}), 200

@routes.route("/request-password-reset", methods=["POST"])
def request_password_reset():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "E-mail é obrigatório"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    # Remove tokens antigos
    PasswordResetToken.query.filter_by(user_id=user.id).delete()

    reset_token = PasswordResetToken(user_id=user.id)
    db.session.add(reset_token)
    db.session.commit()

    reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token.token}"

    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        message = Mail(
            from_email=MAIL_SENDER,
            to_emails=email,
            subject="Recuperação de Senha",
            html_content=f"<p>Clique no link para redefinir sua senha:</p><a href='{reset_link}'>{reset_link}</a>"
        )
        sg.send(message)
    except Exception as e:
        current_app.logger.error(f"Erro ao enviar e-mail: {str(e)}")
        return jsonify({"error": "Erro ao enviar e-mail"}), 500

    return jsonify({"message": "E-mail de recuperação enviado"}), 200

@routes.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    token = data.get("token")
    nova_senha = data.get("nova_senha")

    if not token or not nova_senha:
        return jsonify({"error": "Token e nova senha são obrigatórios"}), 400

    reset_token = PasswordResetToken.query.filter_by(token=token).first()

    if not reset_token:
        return jsonify({"error": "Token inválido"}), 400

    if reset_token.is_expired():
        return jsonify({"error": "Token expirado"}), 400

    user = User.query.get(reset_token.user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    user.senha_hash = generate_password_hash(nova_senha)
    db.session.delete(reset_token)
    db.session.commit()

    return jsonify({"message": "Senha alterada com sucesso"}), 200