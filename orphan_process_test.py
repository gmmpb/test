#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime

def create_orphan():
    """Create a simple orphan process."""
    # Try to detach from process group
    try:
        os.setsid()
    except OSError:
        pass  # Already a session leader12
    
    pid = os.fork()
    
    if pid == 0:
        # Child becomes orphan when parent exits
        try:
            os.setsid()  # Create new session
        except OSError:
            pass
        
        time.sleep(2)  # Let parent exit
        
        # Create marker file
        with open(f"/tmp/orphan_{os.getpid()}.txt", "w") as f:
            f.write(f"Orphan {os.getpid()} created at {datetime.now()}\n")
            f.write(f"PPID: {os.getppid()}\n")
            f.write(f"SID: {os.getsid(0)}\n")
        
        # Run for a while with heartbeat
        for i in range(120):  # Run longer
            time.sleep(5)
            print(f"Orphan {os.getpid()} iteration {i+1}")
            
            # Update marker file to show we're alive
            with open(f"/tmp/orphan_{os.getpid()}.txt", "a") as f:
                f.write(f"Heartbeat {i+1} at {datetime.now()}\n")
        
        # Clean up
        os.remove(f"/tmp/orphan_{os.getpid()}.txt")
    else:
        # Parent exits immediately to create orphan
        print(f"Created child {pid}, parent exiting to make orphan")

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
