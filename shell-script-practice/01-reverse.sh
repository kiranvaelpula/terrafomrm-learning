#!/bin/bash

# Script to reverse a number or string

if [ -z "$1" ]; then
  echo "Usage: $0 <string_or_number>"
  exit 1
fi

input="$1"
reversed=$(echo "$input" | rev)

echo "Original: $input"
echo "Reversed: $reversed"
