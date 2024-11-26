from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)

    # 블루프린트
    from .views import main_views, auth_views, todo_views, others_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(todo_views.bp)
    app.register_blueprint(others_views.bp)

    # 필터
    from .filters import avg_progress
    app.jinja_env.filters['progress'] = avg_progress

    return app
