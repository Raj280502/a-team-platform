from flask import Flask
from backend.app import app

flask_app = Flask(__name__)
flask_app.register_blueprint(app)