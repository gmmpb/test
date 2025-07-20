#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime

def create_orphan():
    """Create a simple orphan process."""
    pid = os.fork()
    
    if pid == 0:
        # Child becomes orphan when parent exits
        time.sleep(2)  # Let parent exit
        
        # Create marker file
        with open(f"/tmp/orphan_{os.getpid()}.txt", "w") as f:
            f.write(f"Orphan {os.getpid()} created at {datetime.now()}\n")
        
        # Run for a while
        for i in range(60):
            time.sleep(5)
            print(f"Orphan {os.getpid()} iteration {i+1}")
        
        # Clean up
        os.remove(f"/tmp/orphan_{os.getpid()}.txt")
        sys.exit(0)
    else:
        # Parent exits immediately to create orphan
        print(f"Created child {pid}, parent exiting to make orphan")
        sys.exit(0)

def list_orphans():
    """Show orphan processes and marker files."""
    print("=== ORPHAN PROCESSES ===")
    os.system("/bin/ps aux | grep python | grep -v grep")
    print("\n=== MARKER FILES ===")
    os.system("ls -la /tmp/orphan_*.txt 2>/dev/null || echo 'No orphan marker files'")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_orphans()
    else:
        create_orphan()
