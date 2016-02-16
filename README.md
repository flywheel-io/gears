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

### The info file

Inside the `v0` folder, include a file called `info.toml`.<br>
This file must be in [toml syntax](https://github.com/toml-lang/toml#example) and have a few keys:

* name: A human-friendly name of the gear.
* url: A URL that points to a project webpage.
* license: Software license of the container

An example `info.toml` file:

```toml
name    = "Example gear"
url     = "http://example.com"
license = "apache"
```

### The input directory

When a gear is executed, an `input` folder will be created relative to the base folder.<br>
If a gear has anything previously existing in the `input` folder it will be removed at launch time.

This folder will contain any input file(s) that the gear should process.<br>
The gear's run script (described later) is expected to discover the folder's contents and run accordingly.

For example, in python one approach would be to use the [glob feature](https://docs.python.org/2/library/glob.html) to find an expected input file.<br>
It’s okay to result in a permanent failure if the script can’t find the files it needs.<br>
Keep in mind that the input files may be arbitrarily named.

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
