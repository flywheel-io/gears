import gears

manifest   = gears.load_json_from_file("gears/manifest.example.json")
invocation = gears.load_json_from_file("gears/invocation.example.json")

print "Validating manifest:"
print gears.format_json(manifest)
print
gears.validate_manifest(manifest)

print "Validating invocation:"
print gears.format_json(invocation)
print
schema = gears.validate_invocation(manifest, invocation)

print "Resulted in invocation schema:"
print gears.format_json(schema)
