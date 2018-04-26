#!/usr/bin/env python

from os import sys, path, listdir
import sys
import jsonschema

# This file is not a package; python gets cranky
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import gears

def header(name):
	sys.stdout.write('Testing ' + name + '...')

	spacing = 80 - 8 - 3 -3 - len(name)
	if spacing > 0:
		sys.stdout.write(' ' * spacing)

	sys.stdout.flush()

def test(name, folder):
	header(name)

	manifest = path.join(folder, 'manifest.json')
	invocation = path.join(folder, 'invocation.json')

	if path.isfile(manifest):
		x = gears.load_json_from_file(manifest)
		gears.validate_manifest(x)
	else:
		raise Exception("Test has no manifest: " + name)

	if path.isfile(invocation):
		y = gears.load_json_from_file(invocation)
		gears.validate_invocation(x, y)

def test_wrap(name, folder, shouldpass):
	e = None

	try:
		test(name, folder)
		if shouldpass:
			print '[X]'
			return

	except jsonschema.exceptions.ValidationError as ex:

		if shouldpass:
			print '[ ]'
			raise ex
		else:
			print '[X]'
			return

	print '[ ]'
	raise Exception('Test should fail but did not: ' + name)

def test_folders():
	base = path.dirname(path.abspath(__file__))

	for f in listdir(base):
		file = path.join(base, f)
		name = f.replace('invalid-', '').replace('valid-', '')

		if path.isdir(file):
			if f.startswith('valid-'):
				test_wrap(name, file, True)
			elif f.startswith('invalid-'):
				test_wrap(name, file, False)
			else:
				raise Exception('Folder is improperly named: ' + f)

def main():
	test_folders()

if __name__ == "__main__":
    main()
