#!/bin/bash

# Check if at least one argument is provided
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <command> [arguments...]"
  exit 1
fi

for i in {1..20}
do
  "$@"
done
