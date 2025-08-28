from flask_sqlalchemy import SQLAlchemy
from routes.consume_routes import consume_bp
from routes.short_circuit_routes import short_circuit_bp
from core.config import Config, engine
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from models.models import Base

from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)
app.register_blueprint(consume_bp)
app.register_blueprint(short_circuit_bp)

db = SQLAlchemy(app)

with app.app_context():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
