from datetime import datetime

from app.extensions import db
from app.models import AdminUser, ServiceGroup, Service, Location, SiteSettings


def _slugify(text):
    import re
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')


def seed_database(app):
    """Populate the database with default data only if empty."""
    _seed_admin(app)
    _seed_settings()
    _seed_groups()
    _seed_locations()
    db.session.commit()


def _seed_admin(app):
    if AdminUser.query.count() == 0:
        user = AdminUser(username=app.config['ADMIN_USERNAME'])
        user.set_password(app.config['ADMIN_PASSWORD'])
        db.session.add(user)
        print('Admin user created. Change the password after first login.')


def _seed_settings():
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
    for key, value in defaults.items():
        if SiteSettings.query.get(key) is None:
            db.session.add(SiteSettings(key=key, value=value))


def _seed_groups():
    if ServiceGroup.query.count() > 0:
        return

    groups = [
        {
            'name': 'Solar Energy Solutions', 'slug': 'solar',
            'icon': 'solar', 'sort_order': 1,
            'short_description': 'On-grid, off-grid and hybrid solar systems with design, '
                                 'installation, service and maintenance across Tamil Nadu.',
            'services': [
                ('Solar Panel Sales', 'sales'),
                ('Solar System Design & Installation', 'sales'),
                ('On-Grid Solar Systems', 'sales'),
                ('Off-Grid Solar Systems', 'sales'),
                ('Hybrid Solar Systems', 'sales'),
                ('Solar Rooftop Systems', 'sales'),
                ('Solar Energy System Service & Maintenance', 'service'),
            ],
        },
        {
            'name': 'Battery Energy Storage Systems', 'slug': 'bess',
            'icon': 'battery', 'sort_order': 2,
            'short_description': 'Energy storage solutions, battery backup systems and '
                                 'solar + BESS for commercial and industrial applications.',
            'services': [
                ('BESS Sales & Installation', 'sales'),
                ('Energy Storage Solutions', 'sales'),
                ('Battery Backup Systems', 'sales'),
                ('Solar + BESS Solutions', 'sales'),
                ('Commercial & Industrial Energy Storage', 'sales'),
            ],
        },
        {
            'name': 'Inverters & Power Backup', 'slug': 'ups',
            'icon': 'bolt', 'sort_order': 3,
            'short_description': 'Inverters, hybrid inverters, UPS systems and battery '
                                 'backup with complete service and maintenance.',
            'services': [
                ('Inverters', 'sales'),
                ('Hybrid Inverters', 'sales'),
                ('Solar Inverters', 'sales'),
                ('UPS Systems', 'sales'),
                ('Online UPS', 'sales'),
                ('Offline UPS', 'sales'),
                ('Battery Systems', 'sales'),
                ('Inverter & UPS Service', 'service'),
            ],
        },
        {
            'name': 'Generator Solutions', 'slug': 'generators',
            'icon': 'engine', 'sort_order': 4,
            'short_description': 'Diesel generators with sales, installation, AMC, '
                                 'servicing and spare parts for all applications.',
            'services': [
                ('Diesel Generators (DG Sets)', 'sales'),
                ('Generator Sales', 'sales'),
                ('Generator Installation', 'sales'),
                ('Generator Commissioning', 'sales'),
                ('Generator AMC', 'service'),
                ('Generator Servicing & Repairs', 'service'),
                ('Generator Maintenance', 'service'),
                ('Generator Spare Parts', 'sales'),
                ('Commercial & Industrial Generator Solutions', 'sales'),
            ],
        },
        {
            'name': 'Agricultural Pump Sets', 'slug': 'pumps',
            'icon': 'water', 'sort_order': 5,
            'short_description': 'Agriculture pump sets and solar water pumping systems '
                                 'with sales, installation, service and maintenance.',
            'services': [
                ('Agriculture Pump Sets', 'sales'),
                ('Solar Water Pumping Systems', 'sales'),
                ('Solar Pump Solutions', 'sales'),
                ('Pump Set Sales', 'sales'),
                ('Pump Installation', 'service'),
                ('Pump Servicing & Maintenance', 'service'),
            ],
        },
        {
            'name': 'Electrical Solutions', 'slug': 'electrical',
            'icon': 'plug', 'sort_order': 6,
            'short_description': 'Electrical equipment, panels, switchgear, cables and '
                                 'accessories for commercial and industrial applications.',
            'services': [
                ('Electrical Equipment', 'sales'),
                ('Electrical Panels', 'sales'),
                ('Cables & Wires', 'sales'),
                ('Switchgear', 'sales'),
                ('Distribution Equipment', 'sales'),
                ('Electrical Accessories', 'sales'),
                ('Commercial Electrical Solutions', 'sales'),
                ('Industrial Electrical Solutions', 'sales'),
            ],
        },
        {
            'name': 'Sales, Service & Maintenance', 'slug': 'service',
            'icon': 'wrench', 'sort_order': 7,
            'short_description': 'Dedicated service and maintenance across all our '
                                 'solutions, including AMC and troubleshooting.',
            'services': [
                ('Solar Service', 'service'),
                ('Generator Service', 'service'),
                ('Inverter & UPS Service', 'service'),
                ('BESS Maintenance', 'service'),
                ('Pump Set Service', 'service'),
                ('Electrical Maintenance', 'service'),
                ('AMC / Annual Maintenance Contracts', 'service'),
                ('Troubleshooting & Repairs', 'service'),
            ],
        },
    ]

    used_slugs = set()
    for g in groups:
        group = ServiceGroup(
            name=g['name'], slug=g['slug'], icon=g['icon'],
            short_description=g['short_description'], sort_order=g['sort_order'], active=True,
        )
        db.session.add(group)
        db.session.flush()
        for sname, stype in g['services']:
            slug = _unique_slug(_slugify(sname), used_slugs)
            db.session.add(Service(
                group_id=group.id, name=sname, slug=slug,
                short_description='', description='', icon='cog',
                sales=(stype == 'sales'), service=(stype == 'service'), active=True,
            ))


def _unique_slug(base, used):
    """Return a unique slug across the whole seed run."""
    slug = base
    n = 2
    while slug in used or Service.query.filter_by(slug=slug).first() is not None:
        slug = f"{base}-{n}"
        n += 1
    used.add(slug)
    return slug


def _seed_locations():
    if Location.query.count() > 0:
        return

    offices = [
        {
            'city': 'Salem', 'state': 'Tamil Nadu', 'location_type': 'office',
            'address': 'Salem, Tamil Nadu',
            'phone': '98940-79090', 'email': 'gvpowerssalem@gmail.com',
            'latitude': 11.6643, 'longitude': 78.1460,
        },
        {
            'city': 'Chennai', 'state': 'Tamil Nadu', 'location_type': 'office',
            'address': 'Chennai, Tamil Nadu',
            'phone': '98940-79095', 'email': 'gvpowers.chennai@gmail.com',
            'latitude': 13.0827, 'longitude': 80.2707,
        },
    ]
    for o in offices:
        db.session.add(Location(**o))

    service_cities = ['Salem', 'Chennai', 'Attur', 'Kallakurichi', 'Vazhapadi']
    for city in service_cities:
        db.session.add(Location(
            city=city, state='Tamil Nadu', location_type='service',
            address='', phone='', email='', active=True,
        ))
