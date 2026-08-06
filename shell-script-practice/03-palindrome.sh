#!/bin/bash

# Script to check if a string/number is a palindrome
# A palindrome reads the same forward and backward
# Examples: "madam", "121", "racecar"

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <string_or_number>"
  exit 1
fi

input="$1"                              # Store original input
reversed=$(echo "$input" | rev)         # Reverse the input using rev command

# Compare original with reversed
if [ "$input" == "$reversed" ]; then
  echo "'$input' is a palindrome"
else
  echo "'$input' is NOT a palindrome"
fi
