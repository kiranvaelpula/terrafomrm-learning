#!/bin/bash

# Script to swap two numbers without using a temporary variable
# Uses arithmetic: a = a + b, b = a - b, a = a - b

# Check if both arguments are provided
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <number1> <number2>"
  exit 1
fi

a=$1             # First number
b=$2             # Second number

echo "Before swap: a=$a, b=$b"

# Swap without temp variable using arithmetic
a=$((a + b))     # a now holds the sum of both
b=$((a - b))     # subtract new a - b gives original a
a=$((a - b))     # subtract new a - new b gives original b

echo "After swap:  a=$a, b=$b"
