#!/bin/bash

# Script to calculate factorial of a number
# Factorial of n = n * (n-1) * (n-2) * ... * 1
# Example: 5! = 5 * 4 * 3 * 2 * 1 = 120

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <number>"
  exit 1
fi

number=$1        # Store the input number
factorial=1      # Initialize result to 1

# Validate that input is a positive number
if [ "$number" -lt 0 ]; then
  echo "Error: Factorial is not defined for negative numbers"
  exit 1
fi

# Loop from 1 to the number, multiplying each time
for (( i=1; i<=number; i++ )); do
  factorial=$((factorial * i))    # Multiply current factorial by i
done

echo "Factorial of $number is: $factorial"
