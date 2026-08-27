from functools import lru_cache
from werkzeug.utils import secure_filename
import os
import uuid

from app.extensions import db


def _setting(key, default=''):
    from app.models import SiteSettings
    return SiteSettings.get(key, default)


def get_settings():
    """Return a dictionary of all site-wide settings with sensible defaults."""
    defaults = {
        'company_name': 'GV POWERS',
        'established': '1997',
        'tagline': 'Energy & Power Solutions Since 1997',
        'hero_headline': 'Powering a Better Future with Reliable Energy Solutions',
        'hero_subheading': 'Solar Energy • Generators • BESS • UPS • Inverters • Electrical Solutions',
        'hero_text': ('Established in 1997, GV POWERS provides energy, power backup and '
                      'electrical solutions with sales and service coverage across Tamil Nadu.'),
        'company_description': (
            'GV POWERS is an established energy and power solutions company serving '
            'customers across Tamil Nadu since 1997. We specialize in Solar Energy Systems, '
            'Diesel Generators, BESS, UPS Systems, Inverters, Agricultural Pump Sets and '
            'Electrical Solutions, supported by sales, installation, service and maintenance '
            'capabilities.'),
        'phone_1': '98940-79090',
        'phone_2': '98940-79095',
        'phone_1_tel': '9894079090',
        'phone_2_tel': '9894079095',
        'whatsapp': '',
        'email_1': 'gvpowerssalem@gmail.com',
        'email_2': 'gvpowers.chennai@gmail.com',
        'service_area': 'Tamil Nadu',
        'stat_projects_completed': '10+',
        'stat_projects_ongoing': '4',
        'stat_ups_sold': '1250+',
        'stat_generators_sold': '1800+',
        'stat_experience': '1997',
    }

    result = {}
    for key, default in defaults.items():
        result[key] = _setting(key, default)
    return result


def get_statistics():
    s = get_settings()
    return {
        'solar_projects_completed': s.get('stat_projects_completed'),
        'solar_projects_ongoing': s.get('stat_projects_ongoing'),
        'ups_sold': s.get('stat_ups_sold'),
        'generators_sold': s.get('stat_generators_sold'),
        'experience_year': s.get('stat_experience'),
        'experience_label': f"Since {s.get('established')}",
    }


def allowed_file(filename):
    from flask import current_app
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS'])


def save_upload(file_storage):
    """Validate and save an uploaded image. Returns relative URL path or None."""
    from flask import current_app
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None

    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    unique = f"{uuid.uuid4().hex}.{ext}"
    folder = current_app.config['UPLOAD_FOLDER']
    file_storage.save(os.path.join(folder, unique))
    return f"{unique}"
