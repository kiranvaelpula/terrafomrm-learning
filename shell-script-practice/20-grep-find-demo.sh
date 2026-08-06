#!/bin/bash

# Script demonstrating grep and find commands
# These are essential for searching files and content

echo "=== GREP Examples ==="
echo ""

# Create a sample file for demonstration
cat > /tmp/sample.txt << 'EOF'
Hello World
hello bash scripting
ERROR: something failed
WARNING: disk space low
INFO: process started
error: connection timeout
This is a test line
EOF

echo "Sample file created. Contents:"
cat /tmp/sample.txt
echo ""
echo "----------------------------"

# 1. Basic grep - search for pattern
echo "1. Lines containing 'error' (case-insensitive):"
grep -i "error" /tmp/sample.txt              # -i = ignore case

echo ""
# 2. grep with line numbers
echo "2. Lines with 'Hello' (with line numbers):"
grep -n "Hello" /tmp/sample.txt              # -n = show line numbers

echo ""
# 3. grep inverted match
echo "3. Lines NOT containing 'error' (case-insensitive):"
grep -iv "error" /tmp/sample.txt             # -v = invert match

echo ""
# 4. grep count matches
echo "4. Count of lines with 'is':"
grep -c "is" /tmp/sample.txt                 # -c = count matching lines

echo ""
echo "=== FIND Examples ==="
echo ""

# 5. Find files by name
echo "5. Find .sh files in current directory:"
find . -name "*.sh" -type f 2>/dev/null | head -5     # -type f = files only

echo ""
# 6. Find files modified in last 7 days
echo "6. Files modified in last 7 days:"
find . -mtime -7 -type f 2>/dev/null | head -5        # -mtime -7 = last 7 days

echo ""
# 7. Find directories
echo "7. Find directories:"
find . -maxdepth 1 -type d 2>/dev/null                # -type d = directories only

# Cleanup
rm -f /tmp/sample.txt
echo ""
echo "Demo complete. Temp file cleaned up."
