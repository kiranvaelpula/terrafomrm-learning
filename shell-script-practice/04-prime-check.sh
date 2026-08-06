#!/bin/bash

# Script to check if a number is prime
# A prime number is only divisible by 1 and itself
# Examples: 2, 3, 5, 7, 11, 13...

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <number>"
  exit 1
fi

number=$1        # Store the input
is_prime=1       # Flag: 1 = prime, 0 = not prime

# Numbers less than 2 are not prime
if [ "$number" -lt 2 ]; then
  is_prime=0
fi

# Check divisibility from 2 to number/2
for (( i=2; i<=number/2; i++ )); do
  if [ $((number % i)) -eq 0 ]; then   # If remainder is 0, it's divisible
    is_prime=0                           # Mark as not prime
    break                                # No need to check further
  fi
done

# Print result based on flag
if [ $is_prime -eq 1 ]; then
  echo "$number is a prime number"
else
  echo "$number is NOT a prime number"
fi
