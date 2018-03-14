import gears

x = gears.load_json_from_file("gears/manifest.example.json")
gears.validate_manifest(x)

y = gears.load_json_from_file("gears/invocation.example.json")
gears.validate_invocation(x, y)
