import os
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, current_app, url_for
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .models import PasswordResetToken, User
from . import db
import bcrypt
import uuid

bp = Blueprint('routes', __name__)

# Rota para registrar novo usuário
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


# Rota para login de usuário
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


# Rota para solicitar recuperação de senha (gera token e envia email)
@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json or {}
    email = data.get("email")
    if not email:
        return jsonify({"Status": "ERRO", "mensagem": "Informe o email"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        # Resposta neutra para não expor existência do email
        return jsonify({"Status": "OK", "mensagem": "Se o email existir, um link foi enviado."}), 200

    # Cria token temporário e salva no banco
    token_entry = PasswordResetToken(user_id=user.id)
    db.session.add(token_entry)
    db.session.commit()

    # Monta o link para reset de senha
    base = os.getenv("FRONTEND_URL", request.host_url.rstrip("/"))
    reset_link = f"{base}/reset-password/{token_entry.token}"

    # Envia email via SendGrid
    try:
        message = Mail(
            from_email=os.getenv("MAIL_SENDER"),
            to_emails=email,
            subject="Recuperação de senha - Gerenciador",
            html_content=f"""
                <p>Olá,</p>
                <p>Recebemos um pedido para redefinir sua senha. Clique no link abaixo (válido 1 hora):</p>
                <p><a href="{reset_link}">{reset_link}</a></p>
                <p>Se você não solicitou, ignore este email.</p>
            """
        )
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)
    except Exception as e:
        current_app.logger.exception("Erro ao enviar e-mail de recuperação")
        return jsonify({"Status": "ERRO", "mensagem": "Erro ao tentar enviar e-mail"}), 500

    return jsonify({"Status": "OK", "mensagem": "Se o email existir, um link foi enviado."}), 200


# Página HTML para o usuário redefinir senha (acessada pelo link do email)
@bp.route('/reset-password/<token>', methods=['GET'])
def reset_password_page(token):
    return render_template("reset_password.html", token=token)


# Endpoint para receber a nova senha e atualizar usuário
@bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    data = request.json or request.form
    new_password = data.get("password")
    if not new_password:
        return jsonify({"Status": "ERRO", "mensagem": "Senha obrigatória"}), 400

    token_entry = PasswordResetToken.query.filter_by(token=token).first()
    if not token_entry or token_entry.is_expired():
        return jsonify({"Status": "ERRO", "mensagem": "Token inválido ou expirado"}), 400

    user = User.query.get(token_entry.user_id)
    if not user:
        return jsonify({"Status": "ERRO", "mensagem": "Usuário não encontrado"}), 404

    # Atualiza a senha com bcrypt
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    user.senha_hash = hashed

    # Remove o token após uso
    db.session.delete(token_entry)
    db.session.commit()

    # Se for browser, mostra mensagem simples
    if request.content_type and "application/json" not in request.content_type:
        return "<h3>Senha alterada com sucesso. Pode fechar esta página.</h3>"

    return jsonify({"Status": "OK", "mensagem": "Senha alterada com sucesso"}), 200