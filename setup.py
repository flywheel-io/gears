from setuptools import setup

setup(
	version      = '0',
	name         = 'generator',
	author       = 'Flywheel-io',
	author_email = 'support@flywheel.io',
	description  = 'Flywheel Gear manifest tool',
	url          = 'https://github.com/flywheel-io/gears',

	packages     = [ 'gear_tools' ],
	package_data = {'gear_tools': ['../spec/manifest.schema.json']},
	install_requires = [ 'jsonschema', 'rfc3987' ],
)
