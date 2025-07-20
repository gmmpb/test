# Self-Hosted GitHub Runner Testing

This repository is designed to test self-hosted GitHub runners and learn about managing orphan processes.

## Project Structure

- `orphan_process_test.py` - Python script that creates orphan processes
- `cleanup_script.py` - Script to clean up orphan processes
- `.github/workflows/` - GitHub Actions workflows for testing

## Setting Up Self-Hosted Runner

### Step 1: Navigate to Repository Settings

1. Go to your GitHub repository
2. Click on "Settings" tab
3. In the left sidebar, click on "Actions" → "Runners"
4. Click "New self-hosted runner"

### Step 2: Download and Configure Runner

Follow the commands provided by GitHub for your operating system (Linux):

```bash
# Download
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# Extract
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Configure (use the token and URL from GitHub)
./config.sh --url https://github.com/YOUR_USERNAME/YOUR_REPO --token YOUR_TOKEN
```

### Step 3: Start the Runner

```bash
# Start the runner
./run.sh

# Or run as a service (recommended for production)
sudo ./svc.sh install
sudo ./svc.sh start
```

## Testing Orphan Processes

The included scripts will help you:

1. Create orphan processes intentionally
2. Identify orphan processes
3. Clean up orphan processes

## Cleanup Commands

```bash
# Find orphan processes created by our test
ps aux | grep python | grep orphan_process_test

# Kill specific processes
pkill -f orphan_process_test

# Clean up using our script
python cleanup_script.py
```
