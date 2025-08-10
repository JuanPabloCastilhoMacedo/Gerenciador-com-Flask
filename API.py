from flask import Flask, request, jsonify
import mysql.connector, bcrypt
import os

app = Flask(__name__)

print("🔍 Rodando o arquivo API.py da pasta correta!")

@app.route("/register", methods=["POST"])
def register():
    dados = request.json
    email = dados.get("email")
    senha = dados.get("senha")

    if not email or not senha:
        return jsonify({"Status": "ERRO", "mensagem": "Email e senha são obrigatórios."})

    db = conectar()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    if cursor.fetchone():
        db.close()
        return jsonify({"Status": "ERRO", "mensagem": "Email já cadastrado."})

    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO usuarios (email, senha_hash) VALUES (%s, %s)", (email, senha_hash.decode()))
    db.commit()
    db.close()

    return jsonify({"Status": "OK", "mensagem": "Registro realizado com sucesso!"})


def conectar():
    return mysql.connector.connect(
        host="yamanote.proxy.rlwy.net",
        user="root",
        password="wMcsHGxbFmIdpMTixKKhWOwsXdRNNUFq",
        database="railway"
    )

@app.route("/", methods=["GET"])
def home():
    return "API do Juan está online 🚀"

@app.route("/login", methods=["POST"])

def login():
    dados = request.json
    email = dados["email"]
    senha = dados["senha"]

    db = conectar()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
    user = cursor.fetchone()
    db.close()

    if user and bcrypt.checkpw(senha.encode(), user["senha_hash"].encode()):
        return jsonify({"Status": "OK", "mensagem": "Login realizado"})
    return jsonify({"Status": "ERRO", "mensagem": "Credenciais inválidas"})

app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
