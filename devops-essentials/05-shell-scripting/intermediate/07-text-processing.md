# Text Processing (grep, sed, awk)

> **Text processing tools are the backbone of shell scripting — they filter, transform, and extract data from files and command outputs.**

---

## 📖 The Big Three

| Tool | Purpose | Think of it as |
|------|---------|---------------|
| **grep** | FIND lines matching a pattern | Ctrl+F (search) |
| **sed** | REPLACE/MODIFY text in a stream | Find & Replace |
| **awk** | EXTRACT and PROCESS columns | Excel for the terminal |

---

## 🔍 grep — Global Regular Expression Print

grep searches for patterns and prints matching lines.

### Basic Usage

```bash
grep "pattern" filename

# Options you'll use daily:
grep -i "error" file.txt         # -i = ignore case (Error, ERROR, error)
grep -n "error" file.txt         # -n = show line numbers
grep -c "error" file.txt         # -c = count matches (just the number)
grep -v "debug" file.txt         # -v = INVERT (show lines WITHOUT pattern)
grep -r "TODO" ./src/            # -r = recursive (search all files in dir)
grep -l "password" *.conf        # -l = list only filenames that match
grep -w "error" file.txt         # -w = whole word (not "errors" or "terror")
grep -A 3 "error" file.txt      # -A 3 = show 3 lines AFTER match
grep -B 2 "error" file.txt      # -B 2 = show 2 lines BEFORE match
grep -C 2 "error" file.txt      # -C 2 = show 2 lines of CONTEXT (before+after)
```

### Regex with grep

```bash
# Extended regex (-E or use 'egrep')
grep -E "error|warning|critical" /var/log/syslog   # OR pattern
grep -E "^[0-9]{4}-" file.txt                       # Lines starting with year
grep -E "\.log$" filelist.txt                       # Lines ending in .log

# Common patterns
grep "^#" config.txt              # Lines starting with # (comments)
grep -v "^#" config.txt           # Lines NOT starting with # (skip comments)
grep -v "^$" config.txt           # Skip empty lines
grep "^$" config.txt              # Find empty lines
grep "192\.168\." hosts.txt       # Find IPs (escape the dots)
```

### DevOps grep Examples

```bash
# Find errors in logs
grep -i "error\|fail\|critical" /var/log/syslog | tail -20

# Find which config files contain a specific setting
grep -rl "listen 80" /etc/nginx/

# Count 500 errors in access log
grep -c " 500 " /var/log/nginx/access.log

# Find all TODO comments in code
grep -rn "TODO\|FIXME\|HACK" ./src/

# Check if user exists
if grep -q "^deploy:" /etc/passwd; then    # -q = quiet (no output, just exit code)
  echo "Deploy user exists"
fi

# Extract IP addresses from log
grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' access.log | sort -u
```

---

## ✂️ sed — Stream Editor

sed reads text line by line, applies transformations, and outputs the result. It DOESN'T modify the original file unless you use `-i`.

### Substitution (Find & Replace)

```bash
# Syntax: sed 's/old/new/' file
#              s = substitute
#              / = delimiter (can use any character like | or #)

# Replace FIRST occurrence on each line
sed 's/error/ERROR/' file.txt

# Replace ALL occurrences on each line (g = global)
sed 's/error/ERROR/g' file.txt

# Replace only on specific line
sed '5s/old/new/' file.txt          # Only line 5
sed '1,10s/old/new/g' file.txt      # Lines 1-10

# Case insensitive replace
sed 's/error/ERROR/gI' file.txt     # I = case insensitive

# Edit file IN-PLACE (modifies original!)
sed -i 's/old/new/g' file.txt
sed -i.bak 's/old/new/g' file.txt   # Creates backup .bak before modifying
```

### Delete Lines

```bash
sed '5d' file.txt                   # Delete line 5
sed '1d' file.txt                   # Delete first line (header)
sed '$d' file.txt                   # Delete last line
sed '1,5d' file.txt                 # Delete lines 1-5
sed '/pattern/d' file.txt           # Delete lines matching pattern
sed '/^$/d' file.txt                # Delete empty lines
sed '/^#/d' file.txt                # Delete comment lines
```

### Print Specific Lines

```bash
sed -n '5p' file.txt                # Print ONLY line 5
sed -n '5,10p' file.txt             # Print lines 5-10
sed -n '/error/p' file.txt          # Print matching lines (like grep)
sed -n '1p' file.txt                # Print first line only
```

### Insert and Append

```bash
sed '3i\New line inserted before line 3' file.txt    # Insert before
sed '3a\New line appended after line 3' file.txt     # Append after
sed '1i\#!/bin/bash' script.txt                      # Add shebang at top
```

### DevOps sed Examples

```bash
# Update config file value
sed -i 's/listen 80/listen 8080/' /etc/nginx/nginx.conf

# Change database host in config
sed -i "s/DB_HOST=.*/DB_HOST=${NEW_DB_HOST}/" .env

# Remove comment from a line (uncomment)
sed -i 's/^#\(server_name\)/\1/' nginx.conf

# Add line after a pattern
sed -i '/\[database\]/a host = 10.0.1.50' config.ini

# Replace port in multiple files
find /etc/nginx -name "*.conf" -exec sed -i 's/:3000/:4000/g' {} \;

# Extract text between two patterns
sed -n '/BEGIN/,/END/p' file.txt
```

---

## 📊 awk — Pattern Scanning and Processing

awk is a mini programming language for processing structured text (columns/fields). It's perfect for log files, CSVs, and command output.

### How awk Sees Text

```
awk splits each line into FIELDS separated by whitespace (or custom delimiter):

Line: "john  25  developer  50000"
       $1    $2  $3         $4
       
$0 = entire line
$1 = first field
$NF = last field
NR = current line number
NF = number of fields
```

### Basic Usage

```bash
# Print specific columns
awk '{print $1}' file.txt                  # First column
awk '{print $1, $3}' file.txt              # First and third column
awk '{print $NF}' file.txt                 # Last column
awk '{print NR, $0}' file.txt              # Line number + entire line

# Custom field separator
awk -F: '{print $1}' /etc/passwd           # -F: sets delimiter to :
awk -F, '{print $2}' data.csv             # CSV (comma delimiter)
awk -F'|' '{print $3}' file.txt           # Pipe delimiter
```

### Conditional Processing

```bash
# Print lines where column 3 > 100
awk '$3 > 100 {print $1, $3}' data.txt

# Print lines matching a pattern
awk '/error/ {print}' log.txt              # Lines containing "error"
awk '!/debug/ {print}' log.txt             # Lines NOT containing "debug"

# Print specific line numbers
awk 'NR==5 {print}' file.txt               # Only line 5
awk 'NR>=10 && NR<=20 {print}' file.txt    # Lines 10-20
```

### Built-in Variables

```bash
awk '{print NR": "$0}' file.txt            # NR = Record (line) number
awk 'END{print NR}' file.txt               # Total line count
awk '{print NF}' file.txt                  # NF = Number of Fields per line
awk -F: '{print $1, "has UID", $3}' /etc/passwd
```

### Calculations

```bash
# Sum a column
awk '{sum += $1} END {print "Total:", sum}' numbers.txt

# Average
awk '{sum += $1; count++} END {print "Avg:", sum/count}' numbers.txt

# Min and Max
awk 'BEGIN{max=0} $1>max{max=$1} END{print "Max:", max}' numbers.txt
```

### DevOps awk Examples

```bash
# Disk usage — find partitions over 80%
df -h | awk 'NR>1 && int($5) > 80 {print "WARNING:", $6, "is", $5, "full"}'

# Top 10 IPs in access log
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# Memory usage of processes
ps aux | awk '{mem += $4} END {print "Total Memory:", mem"%"}'

# Parse docker ps output
docker ps --format "{{.Names}} {{.Status}}" | awk '{print $1, "—", $2, $3}'

# Calculate average response time from log
awk '{sum += $NF; count++} END {printf "Avg response: %.2fms\n", sum/count}' access.log

# Find large files (over 100MB)
find / -type f -exec du -m {} + 2>/dev/null | awk '$1 > 100 {print $1"MB", $2}'
```

---

## 🔧 Other Essential Text Tools

### cut — Simple column extraction

```bash
cut -d: -f1 /etc/passwd              # First field, : delimiter
cut -d, -f2,4 data.csv              # Fields 2 and 4 from CSV
cut -c1-10 file.txt                  # First 10 characters of each line
cut -c5- file.txt                    # From character 5 to end
```

### sort — Sort lines

```bash
sort file.txt                        # Alphabetical sort
sort -n file.txt                     # Numeric sort (1, 2, 10 not 1, 10, 2)
sort -r file.txt                     # Reverse sort
sort -k2 file.txt                    # Sort by 2nd column
sort -k2 -n file.txt                # Sort by 2nd column numerically
sort -t: -k3 -n /etc/passwd         # Sort passwd by UID
sort -u file.txt                     # Sort and remove duplicates
```

### uniq — Remove/count duplicates (input MUST be sorted!)

```bash
sort file.txt | uniq                 # Remove duplicates
sort file.txt | uniq -c              # Count occurrences
sort file.txt | uniq -d              # Show ONLY duplicates
sort file.txt | uniq -u              # Show ONLY unique lines
```

### tr — Translate/delete characters

```bash
echo "hello" | tr 'a-z' 'A-Z'       # HELLO (uppercase)
echo "HELLO" | tr 'A-Z' 'a-z'       # hello (lowercase)
echo "hello   world" | tr -s ' '    # "hello world" (squeeze spaces)
echo "hello:world" | tr ':' '\n'    # Replace : with newline
echo "he11o" | tr -d '0-9'          # "heo" (delete digits)
```

### wc — Word/Line/Character count

```bash
wc -l file.txt                       # Line count
wc -w file.txt                       # Word count
wc -c file.txt                       # Byte count
wc -m file.txt                       # Character count
wc -l < file.txt                     # Line count (no filename in output)
```

---

## 🛠️ Combining Tools (Power of Pipes)

```bash
# Find top 10 largest log files
find /var/log -name "*.log" -exec du -sh {} + | sort -rh | head -10

# Count unique HTTP status codes
awk '{print $9}' access.log | sort | uniq -c | sort -rn

# Find users who logged in most
last | awk '{print $1}' | sort | uniq -c | sort -rn | head -5

# Extract and count error types
grep "ERROR" app.log | sed 's/.*ERROR: //' | sort | uniq -c | sort -rn

# CSV to formatted table
cat data.csv | column -t -s,

# One-liner to find most disk-consuming directories
du -sh /*  2>/dev/null | sort -rh | head -10
```

---

## 🎯 Interview Quick Points

- **grep** = search/filter lines by pattern
- **sed** = stream editor — find/replace, delete/insert lines
- **awk** = column-based processing, calculations, conditionals
- **cut** = simple column extraction (faster than awk for simple cases)
- **sort** = sort lines (use -n for numeric, -k for column)
- **uniq** = deduplicate (requires sorted input!)
- **tr** = character translation/deletion
- **wc** = count lines/words/characters
- `grep -q` for silent checks in if statements
- `sed -i` modifies files in place (dangerous without backup!)
- `awk -F:` sets field separator
- Combine with pipes for powerful one-liners
- Regular expressions power all three tools
