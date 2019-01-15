from __future__ import print_function
import argparse
import json
import sys

from . import generator

arg_parser = argparse.ArgumentParser()
subparsers = arg_parser.add_subparsers()
parser_invoc_schema = subparsers.add_parser('generate-invocation-schema')
parser_invoc_schema.add_argument('manifest', help='path to manifest file')
args = arg_parser.parse_args(sys.argv[1:] or ['--help'])

manifest = generator.load_json_from_file(args.manifest)

print(json.dumps(generator.derive_invocation_schema(manifest)))
