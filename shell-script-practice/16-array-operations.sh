#!/bin/bash

# Script demonstrating array operations in bash
# Arrays store multiple values in a single variable

# Declare an array with values
fruits=("apple" "banana" "cherry" "date" "elderberry")

echo "--- Array Basics ---"
echo "Full array:      ${fruits[@]}"          # [@] expands all elements
echo "First element:   ${fruits[0]}"          # Arrays are 0-indexed
echo "Third element:   ${fruits[2]}"          # Access by index
echo "Array length:    ${#fruits[@]}"         # # gives count of elements
echo "Last element:    ${fruits[-1]}"         # Negative index = from end

echo ""
echo "--- Looping through array ---"
for fruit in "${fruits[@]}"; do               # Loop through each element
  echo "  - $fruit"
done

echo ""
echo "--- Adding elements ---"
fruits+=("fig")                               # += appends to array
fruits+=("grape")
echo "After adding:    ${fruits[@]}"

echo ""
echo "--- Slicing ---"
echo "Elements 1-3:    ${fruits[@]:1:3}"      # Slice: offset 1, count 3

echo ""
echo "--- Removing element ---"
unset fruits[1]                               # Remove element at index 1
echo "After removing index 1: ${fruits[@]}"

echo ""
echo "--- Array with indices ---"
for i in "${!fruits[@]}"; do                  # ${!arr[@]} gives indices
  echo "  Index $i: ${fruits[$i]}"
done
