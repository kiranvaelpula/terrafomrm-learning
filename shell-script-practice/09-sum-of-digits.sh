#!/bin/bash

# Script to find the sum of digits of a number
# Example: 1234 → 1 + 2 + 3 + 4 = 10

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <number>"
  exit 1
fi

number=$1          # Store original number
temp=$number       # Temp copy for processing
sum=0              # Initialize sum

# Extract digits one by one from right to left
while [ $temp -gt 0 ]; do
  digit=$((temp % 10))       # Get last digit (remainder when divided by 10)
  sum=$((sum + digit))       # Add digit to sum
  temp=$((temp / 10))        # Remove last digit (integer division by 10)
done

echo "Sum of digits of $number is: $sum"
