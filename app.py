from flask import Flask
from models import db
from config import Config
from routes import routes

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)