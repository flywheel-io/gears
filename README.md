# gear-sample

A simple Flywheel gear that demonstrates requirements defined in the specification.

### Input
Any number of files.

### Output
A "file_list.txt" containing names of all input files.


---
_Excerpt from the spec..._

## The base directory

To be a flywheel gear, you must have a specific folder in the container: `/flywheel/v0`.<br>
This indicates that it’s a flywheel gear and what version of the spec you’re using.

All following references to folders are assumed to be relative to this folder.<br>
For example, the `input` dir will be located at `/flywheel/v0/input`.

### The manifest

Inside the `v0` folder, include a file called `manifest.json`.

Here's an example manifest that takes two options and one dicom file:

```json
{
	"name": "Example gear",
	"url": "http://example.com",
	"license": "apache",

	"config": {
		"speed": { "type": "number" },
		"label": { "type": "string", "maxLength": 64 }
	},

	"inputs": {
		"dicom": {
			"base": "file",
			"type": { "enum": [ "dicom" ] }
		}
	}
}
```

First, we have a few basic properties:

* name: A human-friendly name of the gear.
* url: A URL that points to a project webpage.
* license: Software license of the container

Each key of `config` must be a [JSON schema](http://json-schema.org) snippet. The example has one option called "speed", which takes any number, and "label", which takes any string up to 64 characters. If you don't have any config options, it's okay to leave this section blank.

Each key of `inputs` specifies a file that the gear will consume. Each should specify `"base": "file"`, then add any further JSON schema constraints as you see fit. These will be matched against our [file data model](https://github.com/scitran/core/wiki/Data-Model,-v2#file-subdocument-only).

The example has named one input, called "dicom", and mandates that the file's type be dicom.<br>
This governs how gears are automatically run, and provides hints to users when running manually.

Note that for now, the manifests only support a single input.

### The input directory and config

When a gear is executed, an `input` folder will be created relative to the base folder.<br>
If a gear has anything previously existing in the `input` folder it will be removed at launch time.

Inside that folder will be a `config.json` that looks very similar to your manifest:

```json
{
	"config": {
		"speed": "30",
		"label": "Cool gear attempt"
	},
	"inputs": {
		"dicom": {
			"name": "my-data.dcm",
			"type": "dicom"
		}
	}
}
```

The config file holds the resultant configuration & file information for the current execution.
A gear can parse this file to figure out what the options are set to and where the files are located.

In this example, the input is called "dicom", and so will be in a folder inside `input` called `dicom`.
The full path would be: `/flywheel/v0/input/dicom/my-data.dcm`.

### The output directory

When a gear is executed, an `output` folder will be created relative to the base folder.<br>
If a gear has anything previously existing in the `output` folder it will be removed at launch time.

The gear should place any files that should be saved into the `output` folder - and only those files.<br>
Anything in the `output` folder when the gear is complete will be saved as a result.

If you don’t want results saved, it’s okay to leave this folder empty.<br>
Do not remove the `output` folder.

### The run script

A gear must include a file called `run` relative to the base folder.<br>
This file must be marked as executable (`chmod +x run`).<br>
It can be a simple bash script, or whatever else that you want.

`run` is called from its directory, with no arguments, and a (mostly) empty environment.<br>
Notably, the `PATH` is set to `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin` for convenience.<br>
If you need any arguments or variables, add them in your script.

The run script is the only entry point used for the gear and must accomplish everything the gear sets out to do.<br>
On success or permanent failure, exit zero. On transient failure, exit non-zero.<br>
This is the only feedback mechanism you have at the moment.
