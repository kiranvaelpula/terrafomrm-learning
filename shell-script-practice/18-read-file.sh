#!/bin/bash

# Script to read a file line by line
# Demonstrates file I/O operations in bash

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <filename>"
  exit 1
fi

filename="$1"              # Store filename

# Check if file exists and is readable
if [ ! -f "$filename" ]; then              # -f checks if it's a regular file
  echo "Error: '$filename' not found"
  exit 1
fi

if [ ! -r "$filename" ]; then              # -r checks if file is readable
  echo "Error: '$filename' is not readable"
  exit 1
fi

echo "--- File: $filename ---"
echo "Lines: $(wc -l < "$filename")"       # wc -l counts lines; < avoids printing filename
echo "Words: $(wc -w < "$filename")"       # wc -w counts words
echo "Chars: $(wc -c < "$filename")"       # wc -c counts characters
echo "----------------------------"
echo ""

# Read file line by line
line_number=1
while IFS= read -r line; do               # IFS= preserves leading whitespace
                                            # -r prevents backslash interpretation
  echo "$line_number: $line"               # Print line number and content
  line_number=$((line_number + 1))
done < "$filename"                          # Redirect file as input to while loop
