#!/bin/bash

# Script to print multiplication table for a given number
# Example: for 5 → 5x1=5, 5x2=10, ... 5x10=50

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <number>"
  exit 1
fi

number=$1          # The number for which table is generated

echo "Multiplication table for $number:"
echo "----------------------------"

# Loop from 1 to 10
for (( i=1; i<=10; i++ )); do
  result=$((number * i))                    # Calculate product
  echo "$number x $i = $result"             # Print formatted result
done
