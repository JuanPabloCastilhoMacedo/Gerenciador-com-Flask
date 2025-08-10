from flask import Flask
from flask_cors import CORS
from routes import task_routes
from config import db, migrate

app = Flask(__name__)
app.config.from_object("config.Config")

CORS(app)

db.init_app(app)
migrate.init_app(app,db)

app.register_blueprint(task_routes)

@app.route("/", methods=["GET"])
def home():
    return "API está online 🚀"


if __name__ == "__main__":
    app.run(debug=True)