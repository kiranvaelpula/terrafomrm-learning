#!/bin/bash

# Script to check if a number is even or odd
# Even numbers are divisible by 2 (remainder = 0)
# Odd numbers have remainder 1 when divided by 2

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <number>"
  exit 1
fi

number=$1                          # Store the input number

# Use modulo operator (%) to check remainder
if [ $((number % 2)) -eq 0 ]; then    # If remainder is 0 when divided by 2
  echo "$number is EVEN"
else                                    # If remainder is 1
  echo "$number is ODD"
fi
