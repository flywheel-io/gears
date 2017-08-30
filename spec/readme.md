# Flywheel Gear Spec (v0.1.2)

This document describes the structure of a Flywheel Gear.

## Structure & behavior of a gear

A Flywheel gear is a tar file (.tar) of a container; the container must include a specific directory that contains two special files.

This tar file can be created from most common container tools (e.g., Docker).

## The base folder

To be a Flywheel gear, the container in the tar file must include a folder named: `/flywheel/v0`.<br>
All following references to folders are relative to this folder.

The `/flywheel/v0` folder must contain two specific files

   * `manifest.json`   - Describes critical properties of how the gear computes.
   * `run`             - Describes how to execute the algorithm in the gear.

The contents of these files are described here.

## The manifest

Here's an example manifest.json that specifies a Flywheel gear which reads one dicom file as input and specifies one configuration parameter. The keys listed in this example are all required, unless marked otherwise.

For other restrictions and required fields, you can view our [manifest schema](manifest.schema.json).<br>
This document is a [JSON schema](http://json-schema.org), which allows for automatic validation of structured documents.

Note, the `// comments` shown below are not JSON syntax and cannot be included in a real manifest file.
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

	// The author of this gear or algorithm.
	"author":  "Flywheel",

	// (Optional) the maintainer, which may be distinct from the algorithm author.
	// Can be the same as the author field if both roles were filled by the same individual.
	"maintainer":  "Nathaniel Kofalt",

	// Must be an OSI-approved SPDX license string or 'Other'. Ref: https://spdx.org/licenses
	"license": "Apache-2.0",

	// Where to go to learn more about the gear. You can leave this blank.
	"url":     "http://example.example",

	// Where to go for the source code, if applicable. You can leave this blank.
	"source":  "http://example.example/code",

	// Options that the gear can use
	"config": {

		// A name for this option to show in the user interface
		"speed": {

			// (Optional) json-schema syntax to provide further guidance
			"type": "integer",
			"minimum": 0,
			"maximum": 3
		}
	},

	// Inputs (files) that the gear consumes
	"inputs": {

		// A label - describes one of the inputs. Used by the user interface and by the run script.
		"dicom": {

			// Specifies that the input is a single file. For now, it's the only type.
			"base": "file",

			// (Optional) json-schema syntax to provide further guidance
			"type": { "enum": [ "dicom" ] }

		}
	}
}
```

### Manifest inputs

Each key of `inputs` specifies an input to the gear.<br>
At this point, the inputs are always files and the `"base": "file"` is part of the specification.

Further constraints are an advanced feature, so feel free to leave this off until you want to pursue it. When present, they will be used to guide the user to give them hints as to which files are probably the right choice. In the example above, we add a constraint describing the `type` of file. File types will be matched against our [file data model](https://github.com/scitran/core/wiki/Data-Model,-v2#file-subdocument-only).

The example has named one input, called "dicom", and requests that the file's type be dicom.

### Manifest configuration

Each key of `config` specifies a configuration option.

Like the inputs, you can add JSON schema constraints as desired. There are no formal restrictions on `config` yet, but we request that you specify a `type` on each key. Please only use scalars: `string`, `integer`, `number`, `boolean`. It's likely these restrictions will be formalized & enforced in a future version of the spec.

The example has named one config option, called "speed", which must be an integer between zero and three.

### The input folder

When a gear is executed, an `input` folder will be created relative to the base folder. If a gear has anything previously existing in the `input` folder it will be removed at launch time.

In this example, the input is called "dicom", and so will be in a folder inside `input` called `dicom`.
The full path would be, for example: `/flywheel/v0/input/dicom/my-data.dcm`.

### The input configuration

If your gear has specified configuration, inside the `/flywheel/v0` folder a `config.json` file will be provided with any settings the user has provided. For example, if your gear uses the example manifest above, and the user sets `speed` to 2, you'd get a file like the following:

```javascript
{
	"config": {
		"speed": 2
	}
}
```

Each configuration key will have been checked server-side against any constraints you specified, so you can be assured that your gear will be provided valid values. In a future revision, this file will also hold information about the gear's input files.

### The output folder

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

## The run script

The `run` file is `/flywheel/v0/run`.<br>
The file must be executable (`chmod +x run`). It can be a bash script, a python function, or any other executable.

The run script is the only entry point used for the gear and must accomplish everything the gear sets out to do. On success or permanent failure, exit zero. On transient failure, exit non-zero.

### The environment for the run script

An important consideration is the environment when the `run` command is executed.
The command will be executed in the folder containing it (`/flywheel/v0`), and with no environment variables save the `PATH`:

````
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
````

Any required environment and path variables should be specified within the script. This can be important if, for example, you're producing a gear from a Dockerfile, as the variables there will not transfer over. We typically specify the path and environment variables in a `.bashrc` file, and source that file at the beginning of the `run` script.

The file is also executed with no arguments. You must specify the inputs to the executables in the `run` script, such as the input file names or flags.

### Networking

At the current time, basic outbound networking may be available to the gear. This is not necessarily guaranteed, and may vary depending on your installation's setup. It is likely that this feature will become opt-in in a future version of the spec.

Be sure to get in touch with us regarding your networking needs - Matlab license checks, for example.<br>
There are no current plans to allow inbound networking.

## Contact

Please don't hesitate to contact us with questions or comments about the spec at support@flywheel.io !
