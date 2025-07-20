#!/usr/bin/env python3
"""
Enhanced Orphan Process Test with Process Group Management

This script demonstrates solutions for managing orphan processes in GitHub Actions
self-hosted runners, based on solutions from:
https://github.com/actions/runner/issues/598
"""

import os
import sys
import time
import signal
import subprocess
from datetime import datetime

def create_orphan_with_process_group():
    """Create an orphan process using process groups for better management."""
    print(f"[{datetime.now()}] Creating orphan process with process group...")
    
    # Create a new process group
    os.setpgrp()
    
    # Create a child process
    pid = os.fork()
    
    if pid == 0:
        # Child process - create its own process group
        try:
            os.setpgrp()
            print(f"[{datetime.now()}] Child process started with PID: {os.getpid()}")
            print(f"[{datetime.now()}] Process group ID: {os.getpgrp()}")
            print(f"[{datetime.now()}] Parent PID: {os.getppid()}")
            
            # Sleep briefly to let parent exit
            time.sleep(2)
            
            print(f"[{datetime.now()}] After parent exit - Child PID: {os.getpid()}")
            print(f"[{datetime.now()}] After parent exit - Parent PID: {os.getppid()}")
            print(f"[{datetime.now()}] Process group ID: {os.getpgrp()}")
            
            # Create a marker file to track this orphan
            marker_file = f"/tmp/orphan_pgroup_marker_{os.getpid()}.txt"
            with open(marker_file, "w") as f:
                f.write(f"Orphan process {os.getpid()} (PGID: {os.getpgrp()}) created at {datetime.now()}\n")
            
            # Long-running process (simulate work)
            for i in range(30):
                time.sleep(5)
                print(f"[{datetime.now()}] Orphan process {os.getpid()} (PGID: {os.getpgrp()}) still running... iteration {i+1}/30")
            
            print(f"[{datetime.now()}] Orphan process {os.getpid()} finishing normally")
            if os.path.exists(marker_file):
                os.remove(marker_file)
            sys.exit(0)
            
        except Exception as e:
            print(f"[{datetime.now()}] Error in child process: {e}")
            sys.exit(1)
    else:
        # Parent process
        print(f"[{datetime.now()}] Parent process created child with PID: {pid}")
        print(f"[{datetime.now()}] Parent process group: {os.getpgrp()}")
        print(f"[{datetime.now()}] Parent process exiting to create orphan...")
        sys.exit(0)

def create_subprocess_with_preexec():
    """Create a subprocess using preexec_fn to set process group."""
    print(f"[{datetime.now()}] Creating subprocess with preexec_fn...")
    
    script_content = '''
import time
import os
import signal
from datetime import datetime

def setup_process_group():
    """Set up process group for this subprocess."""
    os.setpgrp()

# Set up process group
setup_process_group()

print(f"[{datetime.now()}] Subprocess started with PID: {os.getpid()}")
print(f"[{datetime.now()}] Process group ID: {os.getpgrp()}")

# Create marker file
marker_file = f"/tmp/subprocess_pgroup_marker_{os.getpid()}.txt"
with open(marker_file, "w") as f:
    f.write(f"Subprocess {os.getpid()} (PGID: {os.getpgrp()}) created at {datetime.now()}\\n")

# Run for 2 minutes
for i in range(24):
    time.sleep(5)
    print(f"[{datetime.now()}] Subprocess {os.getpid()} (PGID: {os.getpgrp()}) running... iteration {i+1}/24")

print(f"[{datetime.now()}] Subprocess {os.getpid()} finishing")
if os.path.exists(marker_file):
    os.remove(marker_file)
'''
    
    # Write temporary script
    script_path = "/tmp/subprocess_pgroup_script.py"
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # Start subprocess with preexec_fn to set process group
    def preexec_function():
        os.setpgrp()
    
    proc = subprocess.Popen([
        sys.executable, script_path
    ], preexec_fn=preexec_function)
    
    print(f"[{datetime.now()}] Subprocess started with PID: {proc.pid}")
    return proc

def kill_process_group(pgid):
    """Kill an entire process group."""
    try:
        print(f"[{datetime.now()}] Killing process group {pgid}...")
        os.killpg(pgid, signal.SIGTERM)
        time.sleep(2)
        
        # Check if any processes in the group are still alive
        try:
            os.killpg(pgid, 0)  # Send null signal to check if group exists
            print(f"[{datetime.now()}] Process group {pgid} still exists, sending SIGKILL...")
            os.killpg(pgid, signal.SIGKILL)
        except OSError:
            print(f"[{datetime.now()}] Process group {pgid} successfully terminated")
            
    except OSError as e:
        print(f"[{datetime.now()}] Error killing process group {pgid}: {e}")

def list_process_groups():
    """List current process groups related to our test."""
    print(f"\n[{datetime.now()}] Process groups and processes:")
    
    # Show processes with their process group IDs
    os.system("ps axo pid,ppid,pgid,sid,comm,args | grep -E '(python|orphan|subprocess)' | grep -v grep")
    
    print(f"\n[{datetime.now()}] Marker files:")
    os.system("ls -la /tmp/*pgroup_marker*.txt 2>/dev/null || echo 'No process group marker files found'")

def cleanup_all_process_groups():
    """Clean up all process groups created by our tests."""
    print(f"[{datetime.now()}] Cleaning up all test process groups...")
    
    # Find marker files to get process group information
    import glob
    marker_files = glob.glob("/tmp/*pgroup_marker*.txt")
    
    pgids_to_kill = set()
    
    for marker_file in marker_files:
        try:
            with open(marker_file, 'r') as f:
                content = f.read()
                print(f"Found marker: {content.strip()}")
                
                # Extract PGID from content
                if "PGID:" in content:
                    pgid_str = content.split("PGID:")[1].split(")")[0].strip()
                    try:
                        pgid = int(pgid_str)
                        pgids_to_kill.add(pgid)
                    except ValueError:
                        pass
            
            # Remove marker file
            os.remove(marker_file)
            print(f"Removed marker file: {marker_file}")
            
        except Exception as e:
            print(f"Error processing marker file {marker_file}: {e}")
    
    # Kill process groups
    for pgid in pgids_to_kill:
        kill_process_group(pgid)
    
    print(f"[{datetime.now()}] Process group cleanup completed")

def main():
    """Main function to demonstrate process group management."""
    print(f"[{datetime.now()}] Enhanced Orphan Process Test with Process Groups")
    print(f"[{datetime.now()}] Current PID: {os.getpid()}")
    print(f"[{datetime.now()}] Current PGID: {os.getpgrp()}")
    
    # Show initial state
    list_process_groups()
    
    action = sys.argv[1] if len(sys.argv) > 1 else "pgroup_orphan"
    
    if action == "pgroup_orphan":
        create_orphan_with_process_group()
    elif action == "pgroup_subprocess":
        proc = create_subprocess_with_preexec()
        # Give it time to start
        time.sleep(2)
        list_process_groups()
    elif action == "list":
        list_process_groups()
    elif action == "cleanup":
        cleanup_all_process_groups()
    elif action == "kill_group":
        if len(sys.argv) < 3:
            print("Usage: python enhanced_orphan_test.py kill_group <pgid>")
            sys.exit(1)
        pgid = int(sys.argv[2])
        kill_process_group(pgid)
    else:
        print("Usage: python enhanced_orphan_test.py [pgroup_orphan|pgroup_subprocess|list|cleanup|kill_group <pgid>]")
        sys.exit(1)

if __name__ == "__main__":
    main()
