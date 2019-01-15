#!/usr/bin/env python
from __future__ import print_function

import argparse
from os import sys, path, listdir, walk
import fnmatch
import sys
import jsonschema

# This file is not a package; python gets cranky
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import gears

def header(name):
	"""
	Generate a report header, in the vein of common system utilities
	"""

	sys.stdout.write('Testing ' + name + '...')

	spacing = 80 - 8 - 3 -3 - len(name)
	if spacing > 0:
		sys.stdout.write(' ' * spacing)

	# Allows one to observe progress on longer test runs
	sys.stdout.flush()

def run_test(name, manifest, invocation=None):
	"""
	Run a test with a given name, manifest, and optionally invocation.
	Throws on failure.
	"""

	header(name)

	if path.isfile(manifest):
		x = gears.load_json_from_file(manifest)
		gears.validate_manifest(x)
	else:
		raise Exception("Test has no manifest: " + name)

	if invocation is not None and path.isfile(invocation):
		y = gears.load_json_from_file(invocation)
		gears.validate_invocation(x, y)

def run_test_wrap(name, manifest, invocation, shouldpass):
	"""
	Executes run_test in a try/catch, printing a footer with the result.
	"""

	try:
		run_test(name, manifest, invocation)
		if shouldpass:
			print('[X]')
			return

	except jsonschema.exceptions.ValidationError as ex:

		if shouldpass:
			print('[ ]')
			raise ex
		else:
			print('[X]')
			return

	print('[ ]')
	raise Exception('Test should fail but did not: ' + name)

def run_validation_suite(args):
	"""
	Test the generator against each example in the validation suite.
	"""

	base = path.dirname(path.abspath(__file__))

	for f in listdir(base):
		file = path.join(base, f)
		name = f.replace('invalid-', '').replace('valid-', '')

		if path.isdir(file):

			manifest = path.join(file, 'manifest.json')
			invocation = path.join(file, 'invocation.json')

			if f.startswith('valid-'):
				run_test_wrap(name, manifest, invocation, True)
			elif f.startswith('invalid-'):
				run_test_wrap(name, manifest, invocation, False)
			else:
				raise Exception('Folder is improperly named: ' + f)

def run_custom_suite(args):
	"""
	Test the generator against each example in the custom folder.
	All JSON files are assumed to be valid.
	"""

	base = args.path

	for root, dirnames, filenames in walk(base):
		for filename in fnmatch.filter(filenames, '*.json'):

			manifest = path.join(root, filename)
			run_test_wrap(filename, manifest, None, True)

def generate_cli():
	"""
	Generate a simplistic command-line interface.
	"""

	parser = argparse.ArgumentParser()
	commands = parser.add_subparsers()

	validation = commands.add_parser('validation')
	validation.set_defaults(func=run_validation_suite)

	custom = commands.add_parser('custom')
	custom.set_defaults(func=run_custom_suite)
	custom.add_argument('path')

	return parser


def main():
	parser = generate_cli()
	args = parser.parse_args()

	args.func(args)

if __name__ == "__main__":
    main()
