from setuptools import setup

setup(
    version = '0',
    name = 'gears',
    author = 'Flywheel Exchange, LLC',
    author_email = 'support@flywheel.io',
    description  = 'Flywheel Gear tools',
    url = 'https://github.com/flywheel-io/gears',

    packages = ['gears'],
    package_data = {'gears': ['../spec/manifest.schema.json']},
    install_requires = [
        'jsonschema >= 2.5.1',
        'rfc3987 >= 1.3.7'
    ],
)
