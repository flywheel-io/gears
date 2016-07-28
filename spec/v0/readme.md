# Flywheel Gear Spec (v0)

This document describes the structure and lifecycle of a Flywheel Gear.

## Structure & behaviour of a gear

A flywheel gear is simply a tarball of a container with some special files inside it.<br>
These can be created from and used by many common tools such as Docker!

## The base directory

To be a flywheel gear, you must have a specific folder in the container: `/flywheel/v0`.
All following references to folders are assumed to be relative to this folder.

### The manifest

Inside the `v0` folder, include a file called `manifest.json`.

Here's an example manifest that takes a one dicom file.<br>
Note, the `// comments` are not JSON syntax and cannot be included in a real manifest file:

```javascript
{
	// Computer-friendly name; unique for your organization
	"name": "example-gear",

	// Human-friendly name; displayed in user interface
	"label": "Example Gear",

	// A brief description of the gear's purpose; ideally 1-4 sentences
	"description": "A gear that performs a task.",

	// Human-friendly version identifier
	"version": "1.0",

	// The author of this gear.
	"author":  "Flywheel",

	// Must be an OSI-approved SPDX license string or 'Other'. Ref: https://spdx.org/licenses
	"license": "Apache-2.0",

	// Where to go to learn more about the gear.
	"url":     "http://example.com",

	// Where to go for the source code, if applicable. Can be the same as the above url.
	"source":  "http://example.com/code",


	// TBA, leave empty for now
	"config": {

	},

	// inputs (files) that the gear consumes
	"inputs": {

		// a name for this input to show in the user interface
		"dicom": {

			// specifies that the input is a single file. for now, it's the only type.
			"base": "file",

			// (optional) json-schema syntax to provide further guidance
			"type": { "enum": [ "dicom" ] }

		}
	}
}
```

All keys listed are required unless marked otherwise. There are a few restrictions on field length and format; if you are familiar with [JSON schema](http://json-schema.org) you can look at our manifest schema [here](manifest.schema.json).

Each key of `inputs` specifies a file that the gear will consume. Each should specify `"base": "file"`, then add any further JSON schema constraints as you see fit. These will be matched against our [file data model](https://github.com/scitran/core/wiki/Data-Model,-v2#file-subdocument-only). The constraints are an advanced feature, so feel free to leave this off until you want to pursue it. When present, they will be used to guide the user to give them hints as to which files are probably the right choice.

The example has named one input, called "dicom", and requests that the file's type be dicom.

### The input directory

When a gear is executed, an `input` folder will be created relative to the base folder. If a gear has anything previously existing in the `input` folder it will be removed at launch time.

In this example, the input is called "dicom", and so will be in a folder inside `input` called `dicom`.
The full path would be, for example: `/flywheel/v0/input/dicom/my-data.dcm`.

### The output directory

When a gear is executed, an `output` folder will be created relative to the base folder. If a gear has anything previously existing in the `output` folder it will be removed at launch time.

The gear should place any files that it wants saved into the `output` folder - and only those files.
Anything in the `output` folder when the gear is complete will be saved as a result.

If you don’t want results saved, it’s okay to leave this folder empty.<br>
Do not remove the `output` folder.

### Output metadata

Optionally, a gear can provide metadata about the files it produces. This is communicated via creating a `.metadata.json` file in the output folder.

```javascript
{
	"acquisition": {
		"files": [
			{
				"name": "example.nii.gz",
				"type": "nifti",
				"instrument": "mri",
				"metadata": {
					"value1": "foo",
					"value2": "bar"
				}
			}
		]
	}
}
```

If you are familiar with [JSON schema](http://json-schema.org) you can look at our metadata schema [here](https://github.com/scitran/core/blob/master/api/schemas/input/enginemetadata.json) and our related file schema [here](https://github.com/scitran/core/blob/master/api/schemas/input/file.json). In this example, the file `example.nii.gz` (which must exist in the output folder) is specified as being a nifti file from an MRI machine, with a few custom key/value pairs.

If you are curious about the typical file types, you can find a list of them [here](https://github.com/scitran/core/blob/d4da9eb299db9a7c6c27bdee1032d36db7cef919/api/files.py#L245-L269). You can also set metadata on the acquisition itself or its parent containers, though these features are less-used; see the metadata schema for more details.

As you might expect, gears cannot produce "normal" files called `.metadata.json`, and might cause the gear to fail if the file is improperly formed.

### The run script

A gear must include a file called `run` relative to the base folder. This file must be marked as executable (`chmod +x run`). It can be a simple bash script, or whatever else that you want.

`run` is called from its directory, with no arguments, and a (mostly) empty environment. Notably, the `PATH` is set to `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin` for convenience. If you need any arguments or variables, add them in your script.

The run script is the only entry point used for the gear and must accomplish everything the gear sets out to do. On success or permanent failure, exit zero. On transient failure, exit non-zero.

### Networking

At the current time, basic outbound networking may be available to the gear. This is not necessarily guaranteed, and may vary depending on your installation's setup. It is likely that this feature will become opt-in in a future version of the spec.

Be sure to get in touch with us regarding your networking needs - Matlab license checks, for example.<br>
There are no current plans to allow inbound networking.

### Contact

Please don't hesitate to contact us with questions or comments about the spec at support@flywheel.io !
