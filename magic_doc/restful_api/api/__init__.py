import os
from datetime import datetime
from pathlib import Path
from loguru import logger
from .extentions import app, db, migrate, jwt, ma
from magic_doc.restful_api.common.web_hook import before_request

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def init_app_log(config):
    """
    Setup logging
    :param config:  config file
    :return:
    """
    log_path = os.path.join(Path(__file__).parent.parent, "log")
    if not Path(log_path).exists():
        Path(log_path).mkdir(parents=True, exist_ok=True)
    log_level = config.get("LOG_LEVEL")
    log_name = f'log_{datetime.now().strftime("%Y-%m-%d")}.log'
    log_file_path = os.path.join(log_path, log_name)
    logger.add(str(log_file_path), rotation='00:00', encoding='utf-8', level=log_level, enqueue=True)
    return logger


def _register_db(flask_app):
    db.init_app(flask_app)
    with app.app_context():
        db.create_all()


def create_app(config):
    """
    Create and configure an instance of the Flask application
    :param config:
    :return:
    """
    app.static_folder = os.path.join(root_dir, "static")
    if config is None:
        config = {}
    app.config.update(config)
    init_app_log(config)
    # _register_db(app)
    migrate.init_app(app=app, db=db)
    jwt.init_app(app=app)
    ma.init_app(app=app)
    from .analysis import analysis_blue
    app.register_blueprint(analysis_blue)

    app.before_request(before_request)

    return app
