#!/usr/bin/env bash
(
  #
  # Pushes image with default repo and tag name.
  #
  # Assumes 'docker login' already performed.
  #

  # Set cwd
  unset CDPATH
  cd "$( dirname "${BASH_SOURCE[0]}" )"

  docker push flywheel/gear-sample:latest

)
