#!/bin/bash

# Script to print star patterns (right-angle triangle)
# Example for n=5:
# *
# **
# ***
# ****
# *****

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <number_of_rows>"
  exit 1
fi

rows=$1          # Number of rows to print

echo "Right-angle triangle pattern:"
# Outer loop controls rows
for (( i=1; i<=rows; i++ )); do
  # Inner loop prints stars for current row
  for (( j=1; j<=i; j++ )); do
    echo -n "*"             # Print star without newline
  done
  echo ""                   # Move to next line after each row
done

echo ""
echo "Inverted triangle pattern:"
# Inverted: starts with max stars, decreases
for (( i=rows; i>=1; i-- )); do
  for (( j=1; j<=i; j++ )); do
    echo -n "*"
  done
  echo ""
done
