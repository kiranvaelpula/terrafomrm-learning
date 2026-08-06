#!/bin/bash

# Script to display system information
# Useful for quick system health checks

echo "==============================="
echo "       SYSTEM INFORMATION      "
echo "==============================="

echo ""
echo "Hostname:       $(hostname)"                     # Machine name
echo "OS:             $(uname -s)"                     # Operating system name
echo "Kernel:         $(uname -r)"                     # Kernel version
echo "Architecture:   $(uname -m)"                     # CPU architecture (x86_64, arm64, etc.)
echo "Uptime:        $(uptime -p 2>/dev/null || uptime)"  # How long system has been running
echo ""
echo "--- CPU Info ---"
echo "Processors:     $(nproc 2>/dev/null || echo 'N/A')"  # Number of CPU cores
echo ""
echo "--- Memory Info ---"
free -h 2>/dev/null || echo "free command not available"    # Memory usage in human-readable format
echo ""
echo "--- Disk Usage ---"
df -h / 2>/dev/null || echo "df command not available"      # Disk usage for root partition
echo ""
echo "--- Logged In Users ---"
who                                                          # Currently logged in users
echo ""
echo "--- Current Date/Time ---"
echo "$(date)"                                               # Current date and time
