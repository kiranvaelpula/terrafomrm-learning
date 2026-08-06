#!/bin/bash

# Script demonstrating common string operations in bash

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <string>"
  exit 1
fi

input="$1"       # Store the input string

echo "Original string: $input"
echo "----------------------------"

# 1. String length
echo "Length:          ${#input}"                    # ${#var} gives length of variable

# 2. Convert to uppercase
echo "Uppercase:       ${input^^}"                  # ${var^^} converts to uppercase

# 3. Convert to lowercase
echo "Lowercase:       ${input,,}"                  # ${var,,} converts to lowercase

# 4. First character uppercase
echo "Capitalize:      ${input^}"                   # ${var^} capitalizes first char

# 5. Substring extraction
echo "First 3 chars:   ${input:0:3}"                # ${var:offset:length}

# 6. Replace first occurrence
echo "Replace first 'a' with '@': ${input/a/@}"     # ${var/pattern/replacement}

# 7. Replace all occurrences
echo "Replace all 'a' with '@':  ${input//a/@}"     # ${var//pattern/replacement}

# 8. Check if string contains substring
if [[ "$input" == *"hello"* ]]; then                # * wildcards for pattern matching
  echo "Contains 'hello': YES"
else
  echo "Contains 'hello': NO"
fi
