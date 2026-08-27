import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.seed import seed_database  # noqa: E402

app = create_app()

with app.app_context():
    db.create_all()
    seed_database(app)


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 7000)), debug=debug)
