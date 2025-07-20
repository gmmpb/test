#!/bin/bash
# Monitor orphan process cleanup

echo "=== ORPHAN CLEANUP MONITOR ==="
echo "This will show when orphan processes get cleaned up"
echo

while true; do
    echo "--- $(date) ---"
    
    # Show marker files (orphans that were created)
    echo "Marker files (orphans created):"
    ls -la /tmp/orphan_*.txt 2>/dev/null || echo "No marker files"
    
    # Check if any orphan processes are actually running
    echo "Running orphan processes:"
    if /bin/ps aux | grep "orphan_process_test.py" | grep -v grep | grep -v "list"; then
        echo "↑ ORPHAN PROCESSES STILL RUNNING"
    else
        echo "No orphan processes running (cleaned up)"
    fi
    
    echo "Press Ctrl+C to stop monitoring"
    echo
    sleep 5
done
