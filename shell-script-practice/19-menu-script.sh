#!/bin/bash

# Script demonstrating an interactive menu using select and case
# Shows how to build user-interactive scripts

# Function for each menu option
show_date() {
  echo "Current date: $(date)"
}

show_uptime() {
  echo "System uptime: $(uptime)"
}

show_users() {
  echo "Logged in users:"
  who
}

# Display menu using select (built-in menu generator)
echo "==============================="
echo "     SYSTEM ADMIN MENU         "
echo "==============================="

PS3="Choose an option (1-5): "             # PS3 is the prompt for select

select option in "Show Date" "Show Uptime" "Show Users" "Show Disk Usage" "Exit"; do
  case $option in                          # $option holds the selected text
    "Show Date")
      show_date
      ;;
    "Show Uptime")
      show_uptime
      ;;
    "Show Users")
      show_users
      ;;
    "Show Disk Usage")
      df -h                                # -h for human-readable sizes
      ;;
    "Exit")
      echo "Goodbye!"
      break                                # break exits the select loop
      ;;
    *)                                     # Handles invalid selection
      echo "Invalid option. Please try again."
      ;;
  esac
  echo ""                                  # Blank line for readability
  echo "Press Enter to see menu again..."
done
