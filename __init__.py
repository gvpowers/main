import os

from flask import Flask, render_template
from config import Config
from app.extensions import db, migrate, csrf


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.public import routes as public_routes
    from app.admin import routes as admin_routes

    app.register_blueprint(public_routes.bp)
    app.register_blueprint(admin_routes.bp, url_prefix='/admin')

    from app import models  # noqa: F401

    with app.app_context():
        db.create_all()
        _remove_orphan_enquiries_table()

    register_error_handlers(app)
    register_template_filters(app)
    register_context_processors(app)

    return app


def _remove_orphan_enquiries_table():
    """Drop the legacy 'enquiries' table if it still exists in the database.

    The customer enquiry/email system was removed from the application. The old
    table may remain in an existing database; this drops it non-destructively
    without touching projects, services, locations or settings.
    """
    from sqlalchemy import inspect, text
    from app.extensions import db

    inspector = inspect(db.engine)
    if 'enquiries' in inspector.get_table_names():
        with db.engine.begin() as conn:
            conn.execute(text('DROP TABLE IF EXISTS enquiries'))


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500


def register_template_filters(app):
    @app.template_filter('dt')
    def dt(date_obj):
        if date_obj is None:
            return ''
        return date_obj.strftime('%d %b %Y')


def register_context_processors(app):
    from app.models import Location
    from app.services import get_settings, get_statistics
    from app.image_registry import SECTIONS

    @app.context_processor
    def inject_globals():
        return dict(
            settings=get_settings(),
            stats=get_statistics(),
            nav_locations=Location.query.filter_by(active=True).order_by(
                Location.location_type.asc(), Location.city.asc()).all(),
            IMG=SECTIONS,
        )
