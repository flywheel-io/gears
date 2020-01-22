import os
from setuptools import setup

VERSION = os.environ.get('CI_COMMIT_TAG', 0)

setup(
    version = VERSION,
    name = 'flywheel_gears',
    author = 'Flywheel Exchange, LLC',
    author_email = 'support@flywheel.io',
    description  = 'Flywheel Gear tools',
    url = 'https://gitlab.com/flywheel-io/public/gears',

    packages = ['gears'],
    package_data = {'gears': ['../spec/manifest.schema.json']},
    install_requires = [
        'jsonschema >= 2.5.1',
        'rfc3987 >= 1.3.7'
    ],
)
