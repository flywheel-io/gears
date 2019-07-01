# Flywheel Gear Spec (v0.1.9)

This document describes the structure of a Flywheel Gear.

## Structure & behavior of a gear

A Flywheel gear is a tar file (.tar) of a container; the container must include a specific directory that contains two special files.

This tar file can be created from most common container tools (e.g., Docker).

#### Minimum container requirements

The only requirement for the underlying container is that it must be a \*nix system that provides a bash shell on the path.

## The base folder

To be a Flywheel gear, the container in the tar file must include a folder named: `/flywheel/v0`.

All following references to folders are relative to this folder.

The `/flywheel/v0` folder contains two specific files:

   * `manifest.json`   - Describes critical properties of how the gear computes.
   * `run` - (Optional) Describes how to execute the algorithm in the gear. Alternately, use the manifest `command` key.

The contents of these files are described here.

## The manifest

Here's an example manifest.json that specifies a Flywheel gear which reads one dicom file as input and specifies one configuration parameter. The keys listed in this example are all required, unless marked otherwise.

For other restrictions and required fields, you can view our [manifest schema](manifest.schema.json).

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

	// (Optional) Any citations you wish to add.
	"cite":  "",

	// Must be an OSI-approved SPDX license string or 'Other'. Ref: https://spdx.org/licenses
	"license": "Apache-2.0",

	// Where to go to learn more about the gear. You can leave this blank.
	"url": "http://example.example",

	// Where to go for the source code, if applicable. You can leave this blank.
	"source":  "http://example.example/code",

	// (Optional) Environment variables to set for the gear.
	"environment": {

	},

	// (Optional) Command to execute. Ran inside a bash shell.
	"command": "python script.py"

	// Options that the gear can use
	"config": {

		// A name for this option to show in the user interface
		"speed": {
			"type": "integer",

			// (Optional) json-schema syntax to provide further guidance
			"minimum": 0,
			"maximum": 3,

			"description": "How fast do you want the gear to run? Choose 0-3."
		},

		"coordinates": {
			"type": "array",

			"items": {
				"type": "number",

				"minItems": 3,
				"maxItems": 3,
			},

			"description": "A set of 3D coordinates."
		},
	},

	// Inputs that the gear consumes
	"inputs": {

		// A label - describes one of the inputs. Used by the user interface and by the run script.
		"dicom": {

			// Specifies that the input is a single file. For now, it's the only type.
			"base": "file",

			// (Optional) json-schema syntax to provide further guidance
			"type": { "enum": [ "dicom" ] },

			"description": "Any dicom file."
		},

		// A contextual key-value, provided by the environment. Used for values that are generally the same for an entire project.
		// Not guaranteed to be found - the gear should decide if it can continue to run, or exit with an error.
		"matlab_license_code": {
			"base": "context",
		},

		// An API key, specific to this job, with the same access as the user that launched the gear.
		// Useful for aggregations, integrating with an external system, data analysis, or other automated tasks.
		"key": {
			"base": "api-key",

			// (Optional) request that the API key only be allowed read access.
			"read-only": true
		}
	},

	// Capabilities the gear requires. Not necessary unless you need a specific feature.
	"capabilities": [
		"networking"
	],
}
```

### Manifest inputs

Each key of `inputs` specifies an input to the gear.

At this point, the inputs are always files and the `"base": "file"` is part of the specification.

Further constraints are an advanced feature, so feel free to leave this off until you want to pursue it. When present, they will be used to guide the user to give them hints as to which files are probably the right choice. In the example above, we add a constraint describing the `type` of file. File types will be matched against our [file data model](https://github.com/scitran/core/wiki/Data-Model,-v2#file-subdocument-only).

The example has named one input, called "dicom", and requests that the file's type be dicom.

### Manifest configuration

Each key of `config` specifies a configuration option.

Like the inputs, you can add JSON schema constraints as desired. Please specify a `type` on each key. Please only use non-object types: `string`, `integer`, `number`, `boolean`.

The example has named one config option, called "speed", which must be an integer between zero and three, and another called "coordinates", which must be a set of three floats.

In some cases, a configuration option may not have a safe default, and it only makes sense to sometimes omit it entirely. If that is the case, specify `"optional": true` on that config key.

### Contextual values

Context inputs are values that are generally provided by the environment, rather than the human or process running the gear. These are generally values that are incidentally required rather than directly a part of the algorithm - for example, a license key.

It is up to the gear executor to decide how (and if) context is provided. In the Flywheel system, the values can be provided by setting a `context.key-name` value on a container's metadata. For example, you could set `context.matlab_license_code: "AEX"` on the project, and then any gear running in that project with a context input called `matlab_license_code` would receive the value.

Unlike a gear's config values, contexts are not guaranteed to exist _or_ have a specific type or format. It is up to the gear to decide if it can continue, or exit with an error, when a context value does not match what the gear expects. In the example config file below, note that the `found` key can be checked to determine if a value was provided by the environment.

Because context values are not namespaced, it is suggested that you use a specific and descriptive name. The `matlab_license_code` example is a good, self-explanatory key that many gears could likely reuse.


### API keys

It is possible to interact with the Flywheel data hierarchy using our [python](https://flywheel-io.github.io/core/branches/master/python/getting_started.html), [matlab](https://flywheel-io.github.io/core/branches/master/matlab/getting_started.html), and (slated for an overhaul) [golang](https://github.com/flywheel-io/sdk) SDKs.

Generally, you will want to figure out a script that you like, using your normal user API key, before turning it into a gear. To do this, specify an `api-key` type input as show in the example above, and use that value in your gear script.

The key provided will be a special key that has the same access as the running user (not necessarily the gear author), and only work while the job is running. After the job completes, the key is retired. This has write access by default, but you can make it read only by adding `"read-only": true` to the manifest as shown above.

### The input folder

When a gear is executed, an `input` folder will be created relative to the base folder. If a gear has anything previously existing in the `input` folder it will be removed at launch time.

In this example, the input is called "dicom", and so will be in a folder inside `input` called `dicom`.
The full path would be, for example: `/flywheel/v0/input/dicom/my-data.dcm`.

### The input configuration

Inside the `/flywheel/v0` folder a `config.json` file will be provided with any settings the user has provided, and information about provided files. For example, if your gear uses the example manifest above, you'd get a file like the following:

```javascript
{
	"config": {
		"speed": 2,
		"coordinates": [1, 2, 3]
	},
	"inputs" : {
		"dicom" : {
			"base" : "file",
			"hierarchy" : {
				"type" : "acquisition",
				"id" : "5988d38b3b49ee001bde0853"
			},
			"location" : {
				"path" : "/flywheel/v0/input/dicom/example.dcm",
				"name" : "example.dcm"
			},
			"object" : {
				"info" : {},
				"mimetype" : "application/octet-stream",
				"tags" : [],
				"measurements" : [],
				"type" : "dicom",
				"modality" : null,
				"size" : 2913379
			}
		},

		"matlab_license_code": {
			"base": "context",
			"found": true,
			"value": "ABC"
		}
	}
}
```

Each configuration key will have been checked server-side against any constraints you specified, so you can be assured that your gear will be provided valid values.

The `inputs` key will hold useful information about the files. For example, you can use `inputs.dicom.path` to get the full path to the provided file. Also provided will be the location of the input in the hierarchy (if applicable) and any scientific information and metadata known at the time of the job creation. This `inputs` key will currently only be present when running on the Flywheel system.

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

If you are familiar with [JSON schema](http://json-schema.org) you can look at our metadata schema [here](https://github.com/scitran/core/blob/master/swagger/schemas/input/enginemetadata.json) and our related file schema [here](https://github.com/scitran/core/blob/master/swagger/schemas/input/file.json). In this example, the file `example.nii.gz` (which must exist in the output folder) is specified as being a nifti file from an MRI machine, with a few custom key/value pairs.

If you are curious about the typical file types, you can find a list of them [here](https://github.com/scitran/core/blob/d4da9eb299db9a7c6c27bdee1032d36db7cef919/api/files.py#L245-L269). You can also set metadata on the acquisition itself or its parent containers, though these features are less-used; see the metadata schema for more details.

As you might expect, gears cannot produce "normal" files called `.metadata.json`, and might cause the gear to fail if the file is improperly formed.

## The run target and environment

By default, the gear is invoked by running is `/flywheel/v0/run`. The file must be executable (`chmod +x run`). It can be a bash or a Python script, or any other executable. If it is a script, please make sure to include appropriate shebang (`#!`) leading line.

You can change this by setting the `command` key of the manifest.

Your run script is the only entry point used for the gear and must accomplish everything the gear sets out to do. On success, exit zero. If the algorithm encounters a failure, exit non-zero. Ideally, print something out before exiting non-zero, so that your users can check the logs to see why things did not work.

### The environment for the run script

An important consideration is the environment where the `run` command is executed.
The command will be executed in the folder containing it (`/flywheel/v0`), and with no environment variables save the `PATH`:

```
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

Any required environment and path variables should be specified within the script. This can be important if, for example, you're producing a gear from a Dockerfile, as the variables there will not transfer over. We typically specify the path and environment variables in a `.bashrc` file, and source that file at the beginning of the `run` script.

The file is also executed with no arguments. You must specify the inputs to the executables in the `run` script, such as the input file names or flags.

### Capabilities

Capabilities allow for a gear to require certain environmental feature support.

Currently, the only capability available is `networking`, which requires basic outbound networking as described below.
In the future, there will likely be more added: `cuda`, `hpc`, etc.

Do not add speculative capabilities to your manifest.
Executors that do not recognize or cannot provide a specified capability are forbidden from launching the job.

### Networking

Some gears may require outbound networking (to contact the Flywheel API, or for some other purpose).
If your gear needs this, please add the `networking` capability to your manifest as shown in the example above.

For now, all gears are provided some networking, but this is not guaranteed, and may vary depending on your installation's setup.
Adding the capability will future-proof your gear as it is likely this will be changed in the future.

Be sure to get in touch with us regarding your networking needs - Matlab license checks, for example.

There are no plans to allow inbound networking.

### Custom information

There is a final manifest key, `custom`, that is entirely freeform. If you have additional information you'd like to record about your gear - possibly as a result of some toolchain or wrapper - this is a great place to put it.

An example:

```javascript
{
	"name": "gear-with-custom-info",

	// ...

	"custom": {

		"generator": {
			"generated-via": "antlr",
			"credit": "Terence Parr",
			"version": 4
		}
	}
```

In general, try to place your information under a single, top-level key, as in the example above.

#### Reserved custom keys

We use some custom keys for notekeeping, or to enable features that might change in the future. In this way, we can offer functionality without the more onerous process of standardizing it & supporting in perpetuity.

In general, avoid using the custom keys `custom.flywheel` or `custom.gear-builder`. Here's a full list:

* `custom`
  * `docker-image`: This is used to tell the [exchange](https://github.com/flywheel-io/exchange) what docker image to pull and archive.
  * `flywheel`
    * `invalid`: This disables a gear from running entirely (ref [Queue.enqueue_job](https://github.com/flywheel-io/core/blob/81216ca5fa1ccd0fd4685f0bfc9e1a3799a6b96b/api/jobs/queue.py#L161-L162)). Avoid using.
    * `module`: Requests a specific module to execute this gear. Currently only `runsc` is respected; all other values are ignored.
    * `suite`: This identifies a gear as part of a larger suite of tools, such as "FSL 5.0.10".
  * `gear-builder`
    * `image`: The docker image to use as a base for the gear builder, if applicable.
    * `container`: The docker container to use as a base for the gear builder, if applicable.

## Contact

Please don't hesitate to contact us with questions or comments about the spec at support@flywheel.io !
