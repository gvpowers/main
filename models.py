from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class AdminUser(db.Model):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ServiceGroup(db.Model):
    """Top-level business domain (Solar, Generators, UPS, BESS, Pumps, Electrical)."""
    __tablename__ = 'service_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    icon = db.Column(db.String(64), nullable=False, default='bolt')
    short_description = db.Column(db.Text, default='')
    description = db.Column(db.Text, default='')
    active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    services = db.relationship(
        'Service', backref='group', lazy=True,
        order_by='Service.name')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'icon': self.icon,
            'short_description': self.short_description,
            'description': self.description,
            'active': self.active,
            'sort_order': self.sort_order,
        }


class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('service_groups.id'), nullable=True)
    name = db.Column(db.String(160), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False)
    short_description = db.Column(db.Text, default='')
    description = db.Column(db.Text, default='')
    icon = db.Column(db.String(64), default='cog')
    image = db.Column(db.String(255), nullable=True)
    sales = db.Column(db.Boolean, default=True)
    service = db.Column(db.Boolean, default=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    location = db.Column(db.String(160), default='')
    capacity = db.Column(db.String(80), default='')
    client = db.Column(db.String(160), default='')
    description = db.Column(db.Text, default='')
    completion_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='ongoing')  # completed | ongoing
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), default='Tamil Nadu')
    location_type = db.Column(db.String(20), default='service')  # office | service
    address = db.Column(db.Text, default='')
    phone = db.Column(db.String(40), default='')
    email = db.Column(db.String(160), default='')
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SiteSettings(db.Model):
    __tablename__ = 'site_settings'

    key = db.Column(db.String(120), primary_key=True)
    value = db.Column(db.Text, default='')

    @classmethod
    def get(cls, key, default=''):
        row = cls.query.get(key)
        return row.value if row else default

    @classmethod
    def set(cls, key, value):
        row = cls.query.get(key)
        if row:
            row.value = value
        else:
            cls(key=key, value=value)
            db.session.add(row)
        db.session.commit()
