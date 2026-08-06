#!/bin/bash

# Script to create a timestamped backup of a file or directory
# Creates a .tar.gz archive with date in the filename

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <file_or_directory>"
  exit 1
fi

source="$1"                                         # File/directory to backup

# Check if source exists
if [ ! -e "$source" ]; then
  echo "Error: '$source' does not exist"
  exit 1
fi

timestamp=$(date +%Y%m%d_%H%M%S)                   # Generate timestamp (e.g., 20260805_143022)
backup_name="${source}_backup_${timestamp}.tar.gz"  # Construct backup filename

# Create compressed archive
tar -czf "$backup_name" "$source"                   # -c=create, -z=gzip, -f=filename

# Check if tar command succeeded ($? holds last command's exit code)
if [ $? -eq 0 ]; then
  echo "Backup created successfully: $backup_name"
  echo "Size: $(du -h "$backup_name" | cut -f1)"    # Show backup size
else
  echo "Error: Backup failed"
  exit 1
fi
