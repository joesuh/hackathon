from flask import logging, Flask, render_template, request, flash, redirect
from config import Config
from app.extensions import db
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS

csrf = CSRFProtect()
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    csrf.init_app(app)
    CORS(app, resources={r"*": {"origins": "*"}})
    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    csrf.exempt(main_bp)

    # @app.route('/test/')
    # def test_page():
    #     return '<h1>Testing the Flask Application Factory Pattern</h1>'

    return app
