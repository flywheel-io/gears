
"""
Flywheel Gear manifest generator
"""

import argparse
import copy
import json
import os
import sys

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
			# Copy constraints, removing 'base' and 'description' keywords which are not constraints
			value = copy.deepcopy(manifest[kind][key])
			value.pop('base', None)
			value.pop('description', None)
			optional = value.pop('optional', False)

			# The config map holds scalars, while the inputs map holds objects.
			if kind == 'config':
				result['properties'][kind]['properties'][key] = value
			else:
				keyType = manifest[kind][key]['base']
				spec = {}

				if keyType == 'file':
					# Object with any particular properties suggested from the manifest
					# Does not validate the upstream file object schema; that is left to other tools.
					spec = {
						'type': 'object',
						'properties': value, # copy over schema snippet from manifest
					}

				elif keyType == 'api-key':
					# There is currently only an implicit declaration of how api-key type inputs are provisioned.
					# For now, declare an object. Should be improved later.
					spec = {
						'type': 'object'
					}

				elif keyType == 'context':
					# Object with information about a lookup value
					spec = {
						'type':  'object',
						'properties': {
							'base': {
								'type': 'string',
							},
							'found': {
								'type': 'boolean',
							},
							'value': { }, # Context inputs can have any type, or none at all
						},
						'required': [ 'base', 'found', 'value' ]
					}
				else:
					# Whitelist input types
					raise Exception("Unknown input type " + str(keyType))

				# Save into result
				result['properties'][kind]['properties'][key] = spec

			# Require the key be present unless optional flag is set.
			if not optional:
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
	return inv_schema
