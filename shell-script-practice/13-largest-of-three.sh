#!/bin/bash

# Script to find the largest of three numbers
# Uses nested if-else comparison

# Check if all three arguments are provided
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo "Usage: $0 <num1> <num2> <num3>"
  exit 1
fi

a=$1     # First number
b=$2     # Second number
c=$3     # Third number

echo "Numbers: $a, $b, $c"

# Compare: first check if a is largest, then b, else c
if [ $a -ge $b ] && [ $a -ge $c ]; then      # -ge means "greater than or equal"
  echo "Largest: $a"
elif [ $b -ge $a ] && [ $b -ge $c ]; then
  echo "Largest: $b"
else
  echo "Largest: $c"
fi
