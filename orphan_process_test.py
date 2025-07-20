#!/usr/bin/env python3
"""
Orphan Process Test Script

This script demonstrates creating orphan processes and shows how they behave
in a GitHub Actions self-hosted runner environment.
"""

import os
import sys
import time
import signal
import subprocess
from datetime import datetime

def create_orphan_process():
    """Create an orphan process by forking and having parent exit."""
    print(f"[{datetime.now()}] Creating orphan process...")
    
    # Create a child process
    pid = os.fork()
    
    if pid == 0:
        # Child process
        print(f"[{datetime.now()}] Child process started with PID: {os.getpid()}")
        print(f"[{datetime.now()}] Parent PID: {os.getppid()}")
        
        # Sleep briefly to let parent exit
        time.sleep(2)
        
        print(f"[{datetime.now()}] After parent exit - Child PID: {os.getpid()}")
        print(f"[{datetime.now()}] After parent exit - Parent PID: {os.getppid()}")
        
        # Create a marker file to track this orphan
        with open(f"/tmp/orphan_marker_{os.getpid()}.txt", "w") as f:
            f.write(f"Orphan process {os.getpid()} created at {datetime.now()}\n")
        
        # Long-running process (simulate work)
        for i in range(30):
            time.sleep(5)
            print(f"[{datetime.now()}] Orphan process {os.getpid()} still running... iteration {i+1}/30")
        
        print(f"[{datetime.now()}] Orphan process {os.getpid()} finishing normally")
        os.remove(f"/tmp/orphan_marker_{os.getpid()}.txt")
        sys.exit(0)
    else:
        # Parent process
        print(f"[{datetime.now()}] Parent process created child with PID: {pid}")
        print(f"[{datetime.now()}] Parent process exiting to create orphan...")
        sys.exit(0)

def create_background_process():
    """Create a background process using subprocess."""
    print(f"[{datetime.now()}] Creating background process...")
    
    script_content = f'''
import time
import os
from datetime import datetime

print(f"[{{datetime.now()}}] Background process started with PID: {{os.getpid()}}")

# Create marker file
with open(f"/tmp/background_marker_{{os.getpid()}}.txt", "w") as f:
    f.write(f"Background process {{os.getpid()}} created at {{datetime.now()}}\\n")

# Run for 2 minutes
for i in range(24):
    time.sleep(5)
    print(f"[{{datetime.now()}}] Background process {{os.getpid()}} running... iteration {{i+1}}/24")

print(f"[{{datetime.now()}}] Background process {{os.getpid()}} finishing")
os.remove(f"/tmp/background_marker_{{os.getpid()}}.txt")
'''
    
    # Write temporary script
    with open("/tmp/background_script.py", "w") as f:
        f.write(script_content)
    
    # Start background process
    subprocess.Popen([sys.executable, "/tmp/background_script.py"])
    print(f"[{datetime.now()}] Background process started")

def list_current_processes():
    """List current processes related to our test."""
    print(f"\n[{datetime.now()}] Current processes:")
    os.system("ps aux | grep -E '(python|orphan|background)' | grep -v grep")
    
    print(f"\n[{datetime.now()}] Marker files:")
    os.system("ls -la /tmp/*marker*.txt 2>/dev/null || echo 'No marker files found'")

def main():
    """Main function to demonstrate orphan process creation."""
    print(f"[{datetime.now()}] Starting Orphan Process Test")
    print(f"[{datetime.now()}] Current PID: {os.getpid()}")
    
    # Show initial state
    list_current_processes()
    
    action = sys.argv[1] if len(sys.argv) > 1 else "orphan"
    
    if action == "orphan":
        create_orphan_process()
    elif action == "background":
        create_background_process()
        # Give it time to start
        time.sleep(2)
        list_current_processes()
    elif action == "list":
        list_current_processes()
    else:
        print("Usage: python orphan_process_test.py [orphan|background|list]")
        sys.exit(1)

if __name__ == "__main__":
    main()
