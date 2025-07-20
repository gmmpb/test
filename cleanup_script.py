#!/usr/bin/env python3
"""
Cleanup Script for Orphan Processes

This script helps identify and clean up orphan processes created during testing.
"""

import os
import signal
import subprocess
import glob
from datetime import datetime

def find_marker_files():
    """Find all marker files created by test processes."""
    marker_files = glob.glob("/tmp/*marker*.txt")
    return marker_files

def read_marker_file(filepath):
    """Read content of a marker file."""
    try:
        with open(filepath, 'r') as f:
            return f.read().strip()
    except Exception as e:
        return f"Error reading {filepath}: {e}"

def extract_pid_from_marker(filepath):
    """Extract PID from marker filename."""
    try:
        # Extract PID from filename like "/tmp/orphan_marker_12345.txt"
        basename = os.path.basename(filepath)
        pid_str = basename.split('_')[-1].replace('.txt', '')
        return int(pid_str)
    except:
        return None

def is_process_running(pid):
    """Check if a process with given PID is still running."""
    try:
        os.kill(pid, 0)  # Send null signal
        return True
    except OSError:
        return False

def kill_process(pid, force=False):
    """Kill a process with given PID."""
    try:
        signal_type = signal.SIGKILL if force else signal.SIGTERM
        os.kill(pid, signal_type)
        return True
    except OSError as e:
        print(f"Failed to kill process {pid}: {e}")
        return False

def cleanup_orphan_processes():
    """Find and clean up orphan processes created by our tests."""
    print(f"[{datetime.now()}] Starting cleanup of orphan processes...")
    
    # Find marker files
    marker_files = find_marker_files()
    
    if not marker_files:
        print("No marker files found. No orphan processes to clean up.")
        return
    
    print(f"Found {len(marker_files)} marker files:")
    
    cleaned_up = 0
    for marker_file in marker_files:
        print(f"\nProcessing: {marker_file}")
        content = read_marker_file(marker_file)
        print(f"Content: {content}")
        
        pid = extract_pid_from_marker(marker_file)
        if pid is None:
            print(f"Could not extract PID from {marker_file}")
            continue
        
        print(f"Extracted PID: {pid}")
        
        if is_process_running(pid):
            print(f"Process {pid} is still running. Attempting to terminate...")
            
            # Try graceful termination first
            if kill_process(pid, force=False):
                print(f"Sent SIGTERM to process {pid}")
                
                # Wait a bit and check if it's still running
                import time
                time.sleep(2)
                
                if is_process_running(pid):
                    print(f"Process {pid} still running. Forcing termination...")
                    if kill_process(pid, force=True):
                        print(f"Sent SIGKILL to process {pid}")
                    else:
                        print(f"Failed to force kill process {pid}")
                else:
                    print(f"Process {pid} terminated gracefully")
            else:
                print(f"Failed to terminate process {pid}")
        else:
            print(f"Process {pid} is not running")
        
        # Remove marker file
        try:
            os.remove(marker_file)
            print(f"Removed marker file: {marker_file}")
            cleaned_up += 1
        except OSError as e:
            print(f"Failed to remove marker file {marker_file}: {e}")
    
    print(f"\n[{datetime.now()}] Cleanup completed. Processed {cleaned_up} marker files.")

def find_python_processes():
    """Find all Python processes that might be related to our tests."""
    print(f"\n[{datetime.now()}] Finding Python processes related to tests...")
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        relevant_processes = []
        for line in lines:
            if 'python' in line and ('orphan_process_test' in line or 'background_script' in line):
                relevant_processes.append(line)
        
        if relevant_processes:
            print("Found relevant Python processes:")
            for proc in relevant_processes:
                print(f"  {proc}")
        else:
            print("No relevant Python processes found")
        
        return relevant_processes
    except Exception as e:
        print(f"Error finding processes: {e}")
        return []

def force_cleanup_all():
    """Force cleanup of all processes related to our tests."""
    print(f"\n[{datetime.now()}] Performing force cleanup...")
    
    # Kill by process name
    commands = [
        "pkill -f orphan_process_test",
        "pkill -f background_script"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  Command succeeded")
            else:
                print(f"  Command returned {result.returncode}: {result.stderr.strip()}")
        except Exception as e:
            print(f"  Error running command: {e}")
    
    # Remove all marker files
    marker_files = find_marker_files()
    for marker_file in marker_files:
        try:
            os.remove(marker_file)
            print(f"Removed: {marker_file}")
        except Exception as e:
            print(f"Failed to remove {marker_file}: {e}")

def main():
    """Main cleanup function."""
    print(f"[{datetime.now()}] Orphan Process Cleanup Tool")
    print("=" * 50)
    
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "cleanup"
    
    if action == "cleanup":
        cleanup_orphan_processes()
    elif action == "list":
        find_marker_files()
        find_python_processes()
    elif action == "force":
        force_cleanup_all()
    else:
        print("Usage: python cleanup_script.py [cleanup|list|force]")
        print("  cleanup - Clean up orphan processes using marker files")
        print("  list    - List marker files and relevant processes")
        print("  force   - Force kill all related processes")

if __name__ == "__main__":
    main()
