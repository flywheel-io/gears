
"""
Flywheel Gear manifest generator
"""

import argparse
import copy
import json
import os
import sys

import gear_tools

# Normal validation can happen via jsonschema. For validating a schema itself, Draft4Validator is used.
import jsonschema
from jsonschema import Draft4Validator

# jsonschema will silently ignore manifest URI format restriction if not present!
# Ref table at the bottom of https://python-jsonschema.readthedocs.io/en/latest/validate
import rfc3987

master_schema = None

def format_json(d):
	"""
	Convenience method to pretty-print JSON.
	"""
	return json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))

def load_json_from_file(path):
	"""
	Loads a JSON file from disk and returns the parsed map.
	"""

	contents = open(path).read()
	return json.loads(contents)

def get_project_dir():
	"""
	Return the absolute path of this file's directory.
	"""

	return os.path.dirname(os.path.abspath(__file__))

def get_master_schema():
	"""
	Returns the master schema. This will load it from disk and cache in memory.
	"""

	global master_schema

	if master_schema == None:
		master_schema_path = os.path.join(get_project_dir(), "..", "spec", "manifest.schema.json")
		master_schema = load_json_from_file(master_schema_path)

	return master_schema

def validate_manifest(manifest):
	"""
	Validates a gear manifest against the master schema.

	Expect a jsonschema.exceptions.ValidationError error to be raised on failure.
	"""

	schema = get_master_schema()
	jsonschema.validate(manifest, schema)

def derive_invocation_schema(manifest):
	"""
	Creates an invocation schema from a gear manifest.
	This can be used to validate the files and configuration offered to run a gear.
	"""

	validate_manifest(manifest)

	result = {
		'title': 'Invocation manifest for ' + manifest['label'],
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'type': 'object',
		'properties': {
			'config': {
				'type': 'object',
				'properties': {},
				'required': []
			},
			'inputs': {
				'type': 'object',
				'properties': {},
				'required': []
			}
		},
		'required': [ 'config', 'inputs' ]
	}

	# Copy over constraints from manifest
	for kind in ['config', 'inputs']:
		for key in manifest[kind]:
			# Copy constraints, removing 'base' keyword which is not a constraint
			val = copy.deepcopy(manifest[kind][key])
			val.pop('base', None)

			# The config map holds scalars, while the inputs map holds objects.
			if kind == 'config':
				result['properties'][kind]['properties'][key] = val
			else:
				result['properties'][kind]['properties'][key] = {}
				result['properties'][kind]['properties'][key]['properties'] = val
				result['properties'][kind]['properties'][key]['type'] = 'object'

			# Require the key be preset.
			result['properties'][kind]['required'].append(key)

		# After handling each key, remove required array if none are present.
		# Required by jsonschema (minItems 1).
		if len(result['properties'][kind]['required']) == 0:
			result['properties'][kind].pop('required', None)

	# Important: check our work - the result must be a valid schema.
	Draft4Validator.check_schema(result)
	return result

def isolate_file_invocation(invocation, input_name):
	"""
	Given an invocation schema, isolate just a specific file.

	Useful to validate a single input.
	"""

	inv = copy.deepcopy(invocation)
	fis = inv['properties']['inputs']['properties'][input_name]

	fis['title']   = 'Input invocation manifest for ' + input_name
	fis['$schema'] = 'http://json-schema.org/draft-04/schema#'
	fis['type']    = 'object'

	# Important: check our work - the result must be a valid schema.
	Draft4Validator.check_schema(fis)
	return fis

def isolate_config_invocation(invocation):
	"""
	Given an invocation schema, isolate just the config portion.

	Useful to validate configuration options separately from files.
	"""

	inv = copy.deepcopy(invocation)
	fis = inv['properties']['config']

	fis['title']   = 'Config invocation manifest'
	fis['$schema'] = 'http://json-schema.org/draft-04/schema#'
	fis['type']    = 'object'

	# Important: check our work - the result must be a valid schema.
	Draft4Validator.check_schema(fis)
	return fis

def validate_invocation(manifest, invocation):
	"""
	Validates a configuration against a gear's manifest.

	Expect a jsonschema.exceptions.ValidationError error to be raised on failure.
	"""

	inv_schema = derive_invocation_schema(manifest)
	jsonschema.validate(invocation, inv_schema)


def test(): # Can become a test case later :)
	x = load_json_from_file(os.path.join(get_project_dir(), "manifest.example.json"))
	validate_manifest(x)

	y = load_json_from_file(os.path.join(get_project_dir(), "invocation.example.json"))
	validate_invocation(x, y)
