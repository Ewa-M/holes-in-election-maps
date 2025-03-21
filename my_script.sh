#!/bin/bash

# Check if at least one argument is provided
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <command> [arguments...]"
  exit 1
fi

# Run the command once with all the provided arguments
"$@"

# Run the command 9 more times with the same arguments
for i in {1..9}
do
  "$@"
done
