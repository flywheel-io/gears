#!/usr/bin/env sh
set -euo pipefail
set -x

pwd

# Working directory
rm -rf temp; mkdir -p temp; cd temp

# All manifests that have been archived
wget https://github.com/flywheel-io/exchange/archive/master.tar.gz

# Set to "manifests" for every version of every gear (needs modification), or "gears" for latest only.
folder="gears"

# Expand just the manifests
tar -xf master.tar.gz --strip-components 1 exchange-master/$folder

# Count
find $folder/ -type f -name '*.json' | wc -l

# Run test
../examples/test.py custom ./$folder

