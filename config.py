import os

class Config:
    # Usando variável de ambiente DATABASE_URL do Railway, ex:
    # mysql+pymysql://user:pass@host:port/dbname
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:senha@localhost:3306/seubanco"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta")  # opcional, mas recomendado