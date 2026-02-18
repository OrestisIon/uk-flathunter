# Scheduling Flathunter to Run Daily

This guide explains how to set up Flathunter to run automatically every night at 7pm on macOS.

## Prerequisites

1. **Anthropic API Key**: Required for LLM-powered property scoring
   - Visit https://console.anthropic.com/settings/keys
   - Click "Create Key"
   - Give it a descriptive name (e.g., "Flathunter")
   - Copy the API key (starts with `sk-ant-api03-...`)
   - Add it to your `.env` file:
     ```
     LLM_API_KEY=sk-ant-api03-your-key-here
     ```

2. **Python environment**: Ensure all dependencies are installed
   ```bash
   pipenv install
   ```

3. **Configuration**: Verify your `config.yaml` and `.env` are properly configured

## Setup Instructions (macOS)

### 1. Make the run script executable

```bash
chmod +x scripts/run_flathunter.sh
```

### 2. Test the run script manually

Before scheduling, verify the script works:

```bash
./scripts/run_flathunter.sh
```

Check the log file in `~/.flathunter/logs/` to ensure it ran successfully.

### 3. Install the launchd job

First, edit `scripts/com.flathunter.daily.plist` and replace the two placeholders with your actual paths:
- `/YOUR/PROJECT/PATH` → the directory where you cloned this repo (e.g. `/Users/you/flathunter`)
- `YOUR_USERNAME` → your macOS username

Then copy it to your LaunchAgents directory:

```bash
cp scripts/com.flathunter.daily.plist ~/Library/LaunchAgents/
```

### 4. Load the scheduled job

```bash
launchctl load ~/Library/LaunchAgents/com.flathunter.daily.plist
```

### 5. Verify the job is loaded

```bash
launchctl list | grep flathunter
```

You should see `com.flathunter.daily` in the output.

## Managing the Scheduled Job

### Check if the job is running

```bash
launchctl list | grep flathunter
```

### View recent logs

```bash
# View latest run log
ls -lt ~/.flathunter/logs/ | head -5

# Read latest log
tail -100 ~/.flathunter/logs/flathunter_*.log | tail -100
```

### Manually trigger a run (for testing)

```bash
launchctl start com.flathunter.daily
```

### Stop the scheduled job

```bash
launchctl unload ~/Library/LaunchAgents/com.flathunter.daily.plist
```

### Restart the scheduled job (after making changes)

```bash
launchctl unload ~/Library/LaunchAgents/com.flathunter.daily.plist
launchctl load ~/Library/LaunchAgents/com.flathunter.daily.plist
```

## Changing the Schedule

To run at a different time, edit `~/Library/LaunchAgents/com.flathunter.daily.plist`:

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>19</integer>  <!-- Change this (0-23) -->
    <key>Minute</key>
    <integer>0</integer>   <!-- Change this (0-59) -->
</dict>
```

Then reload:

```bash
launchctl unload ~/Library/LaunchAgents/com.flathunter.daily.plist
launchctl load ~/Library/LaunchAgents/com.flathunter.daily.plist
```

## Run Multiple Times Per Day

To run multiple times, create multiple `StartCalendarInterval` entries:

```xml
<key>StartCalendarInterval</key>
<array>
    <dict>
        <key>Hour</key>
        <integer>7</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <dict>
        <key>Hour</key>
        <integer>19</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</array>
```

## Troubleshooting

### Job not running

1. Check if loaded:
   ```bash
   launchctl list | grep flathunter
   ```

2. Check error logs:
   ```bash
   cat ~/.flathunter/logs/launchd.err.log
   ```

3. Verify paths in the plist file are correct:
   ```bash
   cat ~/Library/LaunchAgents/com.flathunter.daily.plist
   ```

### Permission errors

Ensure the script is executable:
```bash
chmod +x scripts/run_flathunter.sh
```

### Environment variables not loading

The `.env` file is loaded by the `run_flathunter.sh` script. Verify:
1. `.env` file exists in the project root
2. Variables are properly formatted (no spaces around `=`)
3. LLM_API_KEY is set

### Python module not found

If you're using a virtual environment, ensure it's activated in `run_flathunter.sh`. The script already checks for `venv` and `.venv` directories.

## Logs

- **Application logs**: `~/.flathunter/logs/flathunter_YYYYMMDD_HHMMSS.log`
- **Launchd stdout**: `~/.flathunter/logs/launchd.out.log`
- **Launchd stderr**: `~/.flathunter/logs/launchd.err.log`

Logs older than 30 days are automatically cleaned up.

## Alternative: Using Cron (Linux/macOS)

If you prefer cron instead of launchd:

```bash
# Edit crontab
crontab -e

# Add this line to run at 7pm daily:
0 19 * * * /Users/path/to/file/run_flathunter.sh
```

Note: On macOS, launchd is preferred over cron as it's more reliable and better integrated with the system.
