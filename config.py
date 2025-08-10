from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
db = SQLAlchemy()
migrate = Migrate()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:wMcsHGxbFmIdpMTixKKhWOwsXdRNNUFq@yamanote.proxy.rlwy.net:36335/railway"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False