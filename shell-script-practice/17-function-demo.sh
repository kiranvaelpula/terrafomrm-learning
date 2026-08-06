#!/bin/bash

# Script demonstrating functions in bash
# Functions let you group reusable code blocks

# --- Function with no arguments ---
greet() {
  echo "Hello! Welcome to shell scripting."    # Simple output
}

# --- Function with arguments ---
add() {
  local num1=$1                  # $1 is first arg passed TO the function
  local num2=$2                  # $2 is second arg; 'local' limits scope to function
  local sum=$((num1 + num2))     # Calculate sum
  echo $sum                      # Return value by printing (bash functions can't return strings)
}

# --- Function with return code ---
is_even() {
  local num=$1
  if [ $((num % 2)) -eq 0 ]; then
    return 0                     # 0 = success/true in bash
  else
    return 1                     # non-zero = failure/false
  fi
}

# --- Function calling another function ---
calculator() {
  local operation=$1
  local a=$2
  local b=$3

  case $operation in             # case is like switch statement
    add)      echo "$a + $b = $((a + b))" ;;
    subtract) echo "$a - $b = $((a - b))" ;;
    multiply) echo "$a * $b = $((a * b))" ;;
    divide)
      if [ $b -eq 0 ]; then
        echo "Error: Division by zero"
      else
        echo "$a / $b = $((a / b))"
      fi
      ;;
    *)        echo "Unknown operation: $operation" ;;    # Default case
  esac
}

# --- Calling the functions ---
echo "=== Function Demo ==="
echo ""

echo "1. Simple function:"
greet                            # Call function (no parentheses needed)

echo ""
echo "2. Function with arguments:"
result=$(add 5 3)                # Capture function output in variable
echo "5 + 3 = $result"

echo ""
echo "3. Function with return code:"
if is_even 4; then               # Use function in if condition
  echo "4 is even"
else
  echo "4 is odd"
fi

echo ""
echo "4. Calculator function:"
calculator add 10 5
calculator subtract 10 5
calculator multiply 10 5
calculator divide 10 5
calculator divide 10 0
