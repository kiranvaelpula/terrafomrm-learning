#!/bin/bash

# Script to generate Fibonacci series up to n terms
# Fibonacci: each number is the sum of the two preceding ones
# Series: 0, 1, 1, 2, 3, 5, 8, 13, 21...

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <number_of_terms>"
  exit 1
fi

n=$1             # Number of terms to generate
a=0              # First term
b=1              # Second term
count=0          # Counter

echo "Fibonacci series up to $n terms:"

while [ $count -lt $n ]; do
  echo -n "$a "              # Print current term (no newline)
  next=$((a + b))            # Calculate next term (sum of previous two)
  a=$b                       # Shift: a becomes b
  b=$next                    # Shift: b becomes the new sum
  count=$((count + 1))       # Increment counter
done

echo ""   # Print newline at the end
