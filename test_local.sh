#!/bin/bash

# Local Test Script for Orphan Process Testing
# This script helps you test the functionality locally before running on GitHub Actions

echo "=== Local Orphan Process Testing Script ==="
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Directory: $(pwd)"
echo

function show_menu() {
    echo "Choose a test to run:"
    echo "1. List current processes and marker files"
    echo "2. Create orphan process"
    echo "3. Create background process"  
    echo "4. Run cleanup (graceful)"
    echo "5. Force cleanup (aggressive)"
    echo "6. Show system info"
    echo "7. Exit"
    echo
}

function list_processes() {
    echo "=== Current State ==="
    python3 orphan_process_test.py list
    echo
}

function create_orphan() {
    echo "=== Creating Orphan Process ==="
    echo "This will create an orphan process that will run for ~2.5 minutes"
    read -p "Continue? (y/N): " confirm
    if [[ $confirm == [yY] ]]; then
        python3 orphan_process_test.py orphan &
        sleep 3
        echo "Orphan process created. Checking state:"
        list_processes
    else
        echo "Cancelled."
    fi
    echo
}

function create_background() {
    echo "=== Creating Background Process ==="
    echo "This will create a background process that runs for ~2 minutes"
    read -p "Continue? (y/N): " confirm
    if [[ $confirm == [yY] ]]; then
        python3 orphan_process_test.py background
        sleep 2
        echo "Background process created. Checking state:"
        list_processes
    else
        echo "Cancelled."
    fi
    echo
}

function run_cleanup() {
    echo "=== Running Graceful Cleanup ==="
    python3 cleanup_script.py cleanup
    echo
}

function force_cleanup() {
    echo "=== Running Force Cleanup ==="
    echo "This will forcefully kill all related processes"
    read -p "Continue? (y/N): " confirm
    if [[ $confirm == [yY] ]]; then
        python3 cleanup_script.py force
    else
        echo "Cancelled."
    fi
    echo
}

function show_system_info() {
    echo "=== System Information ==="
    echo "Hostname: $(hostname)"
    echo "OS: $(uname -a)"
    echo "Python: $(python3 --version)"
    echo "Current processes: $(ps aux | wc -l)"
    echo "Memory usage: $(free -h | grep '^Mem')"
    echo "Disk usage: $(df -h . | tail -1)"
    echo
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice (1-7): " choice
    echo
    
    case $choice in
        1) list_processes ;;
        2) create_orphan ;;
        3) create_background ;;
        4) run_cleanup ;;
        5) force_cleanup ;;
        6) show_system_info ;;
        7) 
            echo "Cleaning up before exit..."
            python3 cleanup_script.py force > /dev/null 2>&1
            echo "Goodbye!"
            exit 0 
            ;;
        *) 
            echo "Invalid choice. Please enter 1-7."
            echo
            ;;
    esac
done
