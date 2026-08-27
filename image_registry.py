"""Central registry of section images used across the GV POWERS public site.

Each entry maps a logical key to a base filename. The actual served files are
the optimized WebP (primary) with a JPEG fallback, and responsive width
variants named ``{base}-{width}.webp|.jpg``.

Stock images live in ``static/images/`` (see ``sources.json`` for license
metadata). Uploaded project/customer images live separately in
``static/images/uploads/`` and are referenced by the project database.
"""
import os
from flask import current_app

# Logical key -> base filename (no extension).
SECTIONS = {
    'hero': 'hero',
    'solar': 'solar',
    'generator': 'generator',
    'bess': 'bess',
    'ups': 'ups',
    'inverter': 'inverter',
    'pump': 'pump',
    'electrical': 'electrical',
    'service': 'service',
    'about': 'about',
}

# Responsive widths (in pixels) available for each image via srcset.
WIDTHS = (800, 1200, 1600)

PLACEHOLDER = 'images/project-placeholder.svg'


def images_dir():
    return os.path.join(current_app.static_folder, 'images')


def exists(base, ext):
    """Return True if the given base+ext exists on disk (any width)."""
    return os.path.exists(os.path.join(images_dir(), f'{base}.{ext}'))


def variants(base):
    """Return (webp_srcset, jpg_srcset) tuples with relative URLs for srcset."""
    static = current_app.static_folder
    webp = []
    jpg = []
    for w in WIDTHS:
        webp.append((f'images/{base}-{w}.webp', w))
        jpg.append((f'images/{base}-{w}.jpg', w))
    return webp, jpg
