from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort

bp = Blueprint('admin', __name__)

from app.extensions import db  # noqa: E402
from app.models import (AdminUser, Service, ServiceGroup, Project, Location,  # noqa: E402
                        SiteSettings)
from app.services import get_settings, save_upload, allowed_file  # noqa: E402


# ---------- Auth helpers ----------

def _login_required():
    if not session.get('admin_logged_in'):
        abort(403)


def _ensure_admin_user():
    from flask import current_app
    if AdminUser.query.count() == 0:
        user = AdminUser(username=current_app.config['ADMIN_USERNAME'])
        user.set_password(current_app.config['ADMIN_PASSWORD'])
        db.session.add(user)
        db.session.commit()


@bp.route('/login', methods=['GET', 'POST'])
def login():
    _ensure_admin_user()
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['admin_logged_in'] = True
            session['admin_username'] = user.username
            flash('Welcome back!', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('admin/login.html')


@bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin.login'))


@bp.route('/')
def index():
    _login_required()
    return redirect(url_for('admin.dashboard'))


@bp.route('/dashboard')
def dashboard():
    _login_required()
    stats = {
        'projects_total': Project.query.count(),
        'projects_completed': Project.query.filter_by(status='completed').count(),
        'projects_ongoing': Project.query.filter_by(status='ongoing').count(),
        'services_total': Service.query.count(),
        'groups_total': ServiceGroup.query.count(),
        'locations_total': Location.query.count(),
    }
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(8).all()
    return render_template('admin/dashboard.html', stats=stats, recent_projects=recent_projects)


# ---------- Projects ----------

@bp.route('/projects')
def projects():
    _login_required()
    items = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('admin/projects.html', items=items)


@bp.route('/projects/add', methods=['GET', 'POST'])
def project_add():
    _login_required()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Project name is required.', 'error')
            return redirect(url_for('admin.project_add'))
        image = save_upload(request.files.get('image')) if request.files.get('image') else None
        project = Project(
            name=name,
            slug=_slugify(name),
            location=request.form.get('location', '').strip(),
            capacity=request.form.get('capacity', '').strip(),
            client=request.form.get('client', '').strip(),
            description=request.form.get('description', '').strip(),
            status=request.form.get('status', 'ongoing'),
            completion_date=_parse_date(request.form.get('completion_date', '')),
            image=image,
        )
        db.session.add(project)
        db.session.commit()
        flash('Project added.', 'success')
        return redirect(url_for('admin.projects'))
    return render_template('admin/project_form.html', item=None)


@bp.route('/projects/<int:pid>/edit', methods=['GET', 'POST'])
def project_edit(pid):
    _login_required()
    project = Project.query.get_or_404(pid)
    if request.method == 'POST':
        project.name = request.form.get('name', '').strip()
        project.location = request.form.get('location', '').strip()
        project.capacity = request.form.get('capacity', '').strip()
        project.client = request.form.get('client', '').strip()
        project.description = request.form.get('description', '').strip()
        project.status = request.form.get('status', 'ongoing')
        project.completion_date = _parse_date(request.form.get('completion_date', ''))
        if request.files.get('image') and request.files['image'].filename:
            new_image = save_upload(request.files['image'])
            if new_image:
                project.image = new_image
        db.session.commit()
        flash('Project updated.', 'success')
        return redirect(url_for('admin.projects'))
    return render_template('admin/project_form.html', item=project)


@bp.route('/projects/<int:pid>/delete', methods=['POST'])
def project_delete(pid):
    _login_required()
    project = Project.query.get_or_404(pid)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted.', 'success')
    return redirect(url_for('admin.projects'))


# ---------- Services ----------

@bp.route('/services')
def services():
    _login_required()
    groups = ServiceGroup.query.order_by(ServiceGroup.sort_order.asc()).all()
    items = Service.query.order_by(Service.name.asc()).all()
    return render_template('admin/services.html', groups=groups, items=items)


def _handle_service_form(service=None):
    name = request.form.get('name', '').strip()
    if not name:
        flash('Service name is required.', 'error')
        return None
    data = dict(
        name=name,
        group_id=int(request.form['group_id']) if request.form.get('group_id') else None,
        short_description=request.form.get('short_description', '').strip(),
        description=request.form.get('description', '').strip(),
        icon=request.form.get('icon', 'cog').strip(),
        sales=bool(request.form.get('sales')),
        service=bool(request.form.get('service')),
        active=bool(request.form.get('active')),
    )
    if service:
        for k, v in data.items():
            setattr(service, k, v)
        service.slug = _slugify(name)
        if request.files.get('image') and request.files['image'].filename:
            new_image = save_upload(request.files['image'])
            if new_image:
                service.image = new_image
    else:
        data['slug'] = _slugify(name)
        if request.files.get('image') and request.files['image'].filename:
            data['image'] = save_upload(request.files['image'])
        service = Service(**data)
        db.session.add(service)
    db.session.commit()
    return service


@bp.route('/services/add', methods=['GET', 'POST'])
def service_add():
    _login_required()
    if request.method == 'POST':
        if _handle_service_form():
            flash('Service added.', 'success')
            return redirect(url_for('admin.services'))
    groups = ServiceGroup.query.order_by(ServiceGroup.sort_order.asc()).all()
    return render_template('admin/service_form.html', item=None, groups=groups)


@bp.route('/services/<int:sid>/edit', methods=['GET', 'POST'])
def service_edit(sid):
    _login_required()
    service = Service.query.get_or_404(sid)
    if request.method == 'POST':
        if _handle_service_form(service):
            flash('Service updated.', 'success')
            return redirect(url_for('admin.services'))
    groups = ServiceGroup.query.order_by(ServiceGroup.sort_order.asc()).all()
    return render_template('admin/service_form.html', item=service, groups=groups)


@bp.route('/services/<int:sid>/toggle', methods=['POST'])
def service_toggle(sid):
    _login_required()
    service = Service.query.get_or_404(sid)
    service.active = not service.active
    db.session.commit()
    flash('Service updated.', 'success')
    return redirect(url_for('admin.services'))


@bp.route('/services/<int:sid>/delete', methods=['POST'])
def service_delete(sid):
    _login_required()
    service = Service.query.get_or_404(sid)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted.', 'success')
    return redirect(url_for('admin.services'))


# ---------- Service Groups ----------

@bp.route('/service-groups/add', methods=['POST'])
def group_add():
    _login_required()
    name = request.form.get('name', '').strip()
    if name:
        group = ServiceGroup(
            name=name,
            slug=_slugify(name),
            icon=request.form.get('icon', 'bolt').strip() or 'bolt',
            short_description=request.form.get('short_description', '').strip(),
            sort_order=int(request.form.get('sort_order', 0) or 0),
        )
        db.session.add(group)
        db.session.commit()
        flash('Group added.', 'success')
    return redirect(url_for('admin.services'))


@bp.route('/service-groups/<int:gid>/delete', methods=['POST'])
def group_delete(gid):
    _login_required()
    group = ServiceGroup.query.get_or_404(gid)
    db.session.delete(group)
    db.session.commit()
    flash('Group deleted.', 'success')
    return redirect(url_for('admin.services'))


# ---------- Locations ----------

@bp.route('/locations')
def locations():
    _login_required()
    items = Location.query.order_by(Location.location_type.asc(), Location.city.asc()).all()
    return render_template('admin/locations.html', items=items)


@bp.route('/locations/add', methods=['POST'])
def location_add():
    _login_required()
    city = request.form.get('city', '').strip()
    if not city:
        flash('City name is required.', 'error')
        return redirect(url_for('admin.locations'))
    location = Location(
        city=city,
        state=request.form.get('state', 'Tamil Nadu').strip(),
        location_type=request.form.get('location_type', 'service'),
        address=request.form.get('address', '').strip(),
        phone=request.form.get('phone', '').strip(),
        email=request.form.get('email', '').strip(),
        latitude=_parse_float(request.form.get('latitude', '')),
        longitude=_parse_float(request.form.get('longitude', '')),
        active=bool(request.form.get('active')),
    )
    db.session.add(location)
    db.session.commit()
    flash('Location added.', 'success')
    return redirect(url_for('admin.locations'))


@bp.route('/locations/<int:lid>/edit', methods=['POST'])
def location_edit(lid):
    _login_required()
    location = Location.query.get_or_404(lid)
    location.city = request.form.get('city', '').strip()
    location.state = request.form.get('state', 'Tamil Nadu').strip()
    location.location_type = request.form.get('location_type', 'service')
    location.address = request.form.get('address', '').strip()
    location.phone = request.form.get('phone', '').strip()
    location.email = request.form.get('email', '').strip()
    location.latitude = _parse_float(request.form.get('latitude', ''))
    location.longitude = _parse_float(request.form.get('longitude', ''))
    location.active = bool(request.form.get('active'))
    db.session.commit()
    flash('Location updated.', 'success')
    return redirect(url_for('admin.locations'))


@bp.route('/locations/<int:lid>/delete', methods=['POST'])
def location_delete(lid):
    _login_required()
    location = Location.query.get_or_404(lid)
    db.session.delete(location)
    db.session.commit()
    flash('Location deleted.', 'success')
    return redirect(url_for('admin.locations'))


# ---------- Settings ----------

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    _login_required()
    if request.method == 'POST':
        for key in [
            'company_name', 'established', 'tagline',
            'hero_headline', 'hero_subheading', 'hero_text',
            'company_description',
            'phone_1', 'phone_2', 'phone_1_tel', 'phone_2_tel', 'whatsapp',
            'email_1', 'email_2', 'service_area',
            'stat_projects_completed', 'stat_projects_ongoing',
            'stat_ups_sold', 'stat_generators_sold', 'stat_experience',
        ]:
            val = request.form.get(key, '').strip()
            SiteSettings.set(key, val)
        flash('Settings saved.', 'success')
        return redirect(url_for('admin.settings'))
    return render_template('admin/settings.html', settings=get_settings())


# ---------- Password change ----------

@bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    _login_required()
    if request.method == 'POST':
        current = request.form.get('current_password', '')
        new = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        if new != confirm:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('admin.change_password'))
        if len(new) < 6:
            flash('New password must be at least 6 characters.', 'error')
            return redirect(url_for('admin.change_password'))
        user = AdminUser.query.filter_by(username=session['admin_username']).first()
        if not user or not user.check_password(current):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('admin.change_password'))
        user.set_password(new)
        db.session.commit()
        flash('Password changed successfully.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/change_password.html')


# ---------- Helpers ----------

def _slugify(text):
    import re
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')


def _parse_date(value):
    from datetime import datetime
    try:
        return datetime.strptime(value, '%Y-%m-%d').date() if value else None
    except ValueError:
        return None


def _parse_float(value):
    try:
        return float(value) if value else None
    except ValueError:
        return None
