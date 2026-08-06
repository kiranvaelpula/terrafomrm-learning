#!/bin/bash

# Script to check if a number is an Armstrong number
# An Armstrong number equals the sum of its digits each raised to the power of digit count
# Example: 153 = 1^3 + 5^3 + 3^3 = 1 + 125 + 27 = 153

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <number>"
  exit 1
fi

number=$1                          # Store original number
temp=$number                       # Temp copy for processing
sum=0                              # Will hold sum of powered digits
digits=${#number}                  # Count number of digits using string length

# Extract each digit and add its power to sum
while [ $temp -gt 0 ]; do
  digit=$((temp % 10))             # Get last digit using modulo
  power=1                          # Initialize power calculation

  # Calculate digit^digits manually
  for (( i=0; i<digits; i++ )); do
    power=$((power * digit))
  done

  sum=$((sum + power))             # Add powered digit to sum
  temp=$((temp / 10))              # Remove last digit
done

# Compare sum with original number
if [ $sum -eq $number ]; then
  echo "$number is an Armstrong number"
else
  echo "$number is NOT an Armstrong number"
fi
