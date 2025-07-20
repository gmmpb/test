#!/bin/bash

# GitHub Actions Self-Hosted Runner Cleanup Script
# Based on solutions from: https://github.com/actions/runner/issues/598
#
# This script should be run before/after GitHub Actions jobs to clean up
# orphan processes and prevent resource leaks.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/runner_cleanup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cleanup_orphan_processes() {
    log "=== Cleaning up orphan processes ==="
    
    # Method 1: Use our Python cleanup script
    if [[ -f "$SCRIPT_DIR/cleanup_script.py" ]]; then
        log "Running Python cleanup script..."
        python3 "$SCRIPT_DIR/cleanup_script.py" force || log "Python cleanup had warnings"
    fi
    
    # Method 2: Use enhanced process group cleanup
    if [[ -f "$SCRIPT_DIR/enhanced_orphan_test.py" ]]; then
        log "Running enhanced process group cleanup..."
        python3 "$SCRIPT_DIR/enhanced_orphan_test.py" cleanup || log "Enhanced cleanup had warnings"
    fi
    
    # Method 3: Kill specific process patterns (be careful with this!)
    log "Killing processes by pattern..."
    
    # Kill orphan test processes
    pkill -f "orphan_process_test" || log "No orphan_process_test processes found"
    pkill -f "background_script" || log "No background_script processes found"
    pkill -f "subprocess_pgroup_script" || log "No subprocess_pgroup_script processes found"
    
    # Clean up temporary files
    log "Cleaning up temporary files..."
    rm -f /tmp/*marker*.txt || log "No marker files to clean"
    rm -f /tmp/background_script.py || log "No background script to clean"
    rm -f /tmp/subprocess_pgroup_script.py || log "No subprocess script to clean"
}

cleanup_process_groups() {
    log "=== Cleaning up process groups ==="
    
    # Find and kill process groups that might contain orphaned processes
    # This is more aggressive - use with caution
    
    # Get current runner process
    RUNNER_PID=$(pgrep -f "Runner.Listener" || echo "")
    if [[ -n "$RUNNER_PID" ]]; then
        RUNNER_PGID=$(ps -o pgid= -p "$RUNNER_PID" | tr -d ' ')
        log "Runner process PID: $RUNNER_PID, PGID: $RUNNER_PGID"
        
        # Find child process groups of the runner
        # This is a more sophisticated approach
        log "Looking for child process groups..."
        ps axo pid,ppid,pgid,comm | grep -v "$$" | while read pid ppid pgid comm; do
            # Skip if this is the runner's main process group
            if [[ "$pgid" != "$RUNNER_PGID" ]] && [[ "$comm" =~ (python|node) ]]; then
                log "Found potential orphan process group: PID=$pid, PPID=$ppid, PGID=$pgid, COMM=$comm"
                # Uncomment the next line to actually kill these groups (be careful!)
                # kill -TERM -"$pgid" 2>/dev/null || log "Could not kill process group $pgid"
            fi
        done
    else
        log "Runner process not found"
    fi
}

show_process_tree() {
    log "=== Current Process Tree ==="
    
    # Show process tree to understand what's running
    if command -v pstree >/dev/null 2>&1; then
        pstree -p $$ || log "Could not show process tree"
    else
        log "pstree not available, showing ps output:"
        ps auxf | grep -E "(python|runner|github)" | grep -v grep || log "No relevant processes found"
    fi
}

monitor_resources() {
    log "=== Resource Usage ==="
    
    # Show memory usage
    log "Memory usage:"
    free -h
    
    # Show process count
    PROC_COUNT=$(ps aux | wc -l)
    log "Total processes: $PROC_COUNT"
    
    # Show python processes specifically
    PYTHON_PROC_COUNT=$(ps aux | grep python | grep -v grep | wc -l)
    log "Python processes: $PYTHON_PROC_COUNT"
    
    # Show disk usage in /tmp
    log "Disk usage in /tmp:"
    du -sh /tmp/* 2>/dev/null | sort -hr | head -10 || log "No files in /tmp"
}

# Main cleanup function
main() {
    local action="${1:-cleanup}"
    
    log "Starting runner cleanup script with action: $action"
    log "Script directory: $SCRIPT_DIR"
    log "Current user: $(whoami)"
    log "Current PID: $$"
    log "Current PGID: $(ps -o pgid= -p $$ | tr -d ' ')"
    
    case "$action" in
        "cleanup")
            cleanup_orphan_processes
            ;;
        "aggressive")
            cleanup_orphan_processes
            cleanup_process_groups
            ;;
        "monitor")
            show_process_tree
            monitor_resources
            ;;
        "full")
            show_process_tree
            monitor_resources
            cleanup_orphan_processes
            cleanup_process_groups
            show_process_tree
            monitor_resources
            ;;
        *)
            echo "Usage: $0 [cleanup|aggressive|monitor|full]"
            echo "  cleanup    - Basic orphan process cleanup"
            echo "  aggressive - Cleanup orphan processes and process groups"
            echo "  monitor    - Show current process tree and resources"
            echo "  full       - Monitor, cleanup, and monitor again"
            exit 1
            ;;
    esac
    
    log "Runner cleanup script completed"
}

# Run main function
main "$@"
