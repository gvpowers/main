from flask import (Blueprint, render_template, url_for)

bp = Blueprint('public', __name__)

from app.models import (Project, Service, ServiceGroup, Location)  # noqa: E402
from app.services import get_settings, get_statistics  # noqa: E402


def _active_services():
    return Service.query.filter_by(active=True).order_by(Service.name).all()


@bp.route('/')
def home():
    projects_completed = Project.query.filter_by(status='completed').order_by(
        Project.created_at.desc()).limit(6).all()
    projects_ongoing = Project.query.filter_by(status='ongoing').order_by(
        Project.created_at.desc()).limit(6).all()
    groups = ServiceGroup.query.filter_by(active=True).order_by(
        ServiceGroup.sort_order.asc(), ServiceGroup.name.asc()).all()
    stats = get_statistics()
    return render_template(
        'home.html',
        groups=groups,
        stats=stats,
        projects_completed=projects_completed,
        projects_ongoing=projects_ongoing,
    )


@bp.route('/about')
def about():
    offices = Location.query.filter_by(active=True, location_type='office').order_by(
        Location.city.asc()).all()
    service_locations = Location.query.filter_by(active=True, location_type='service').order_by(
        Location.city.asc()).all()
    return render_template('about.html', offices=offices, service_locations=service_locations)


@bp.route('/services')
def services():
    groups = ServiceGroup.query.filter_by(active=True).order_by(
        ServiceGroup.sort_order.asc(), ServiceGroup.name.asc()).all()
    return render_template('services.html', groups=groups)


@bp.route('/solar')
def solar():
    projects_completed = Project.query.filter_by(status='completed').order_by(
        Project.created_at.desc()).limit(6).all()
    projects_ongoing = Project.query.filter_by(status='ongoing').order_by(
        Project.created_at.desc()).limit(6).all()
    return render_template('solar.html', projects_completed=projects_completed,
                           projects_ongoing=projects_ongoing)


@bp.route('/generators')
def generators():
    return render_template('generators.html')


@bp.route('/ups-inverters')
def ups():
    return render_template('ups.html')


@bp.route('/bess')
def bess():
    return render_template('bess.html')


@bp.route('/pumps')
def pumps():
    return render_template('pumps.html')


@bp.route('/electrical')
def electrical():
    return render_template('electrical.html')


@bp.route('/projects')
def projects():
    completed = Project.query.filter_by(status='completed').order_by(
        Project.completion_date.desc().nulls_last(), Project.created_at.desc()).all()
    ongoing = Project.query.filter_by(status='ongoing').order_by(
        Project.created_at.desc()).all()
    return render_template('projects.html', completed=completed, ongoing=ongoing)


@bp.route('/contact')
def contact():
    services_list = Service.query.filter_by(active=True).order_by(Service.name).all()
    offices = Location.query.filter_by(active=True, location_type='office').order_by(
        Location.city.asc()).all()
    service_locations = Location.query.filter_by(active=True, location_type='service').order_by(
        Location.city.asc()).all()
    settings = get_settings()
    return render_template(
        'contact.html',
        services_list=services_list,
        offices=offices,
        service_locations=service_locations,
        settings=settings,
    )
