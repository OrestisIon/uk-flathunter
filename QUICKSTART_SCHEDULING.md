# Quick Start: Daily Scheduled Runs

## Step 1: Get Your Anthropic API Key

1. Go to https://console.anthropic.com/settings/keys
2. Log in or create an account
3. Click "Create Key" button
4. Give it a name (e.g., "Flathunter")
5. Copy the API key (it will look like `sk-ant-api03-...`)

**Important**: Save this key immediately - you won't be able to see it again!

## Step 2: Add API Key to .env File

Edit your `.env` file and add:

```bash
LLM_API_KEY=sk-ant-api03-your-actual-key-here
LLM_MODEL=claude-sonnet-4.5-20250929
```

## Step 3: Test the App Manually

Run the app once to make sure everything works:

```bash
python3 flathunt.py --config config.yaml
```

If it works, you should see it crawling properties and potentially sending notifications.

## Step 4: Install the Scheduled Job

Run these commands:

```bash
# Copy the launch agent configuration
cp com.flathunter.daily.plist ~/Library/LaunchAgents/

# Load the scheduled job
launchctl load ~/Library/LaunchAgents/com.flathunter.daily.plist

# Verify it's loaded
launchctl list | grep flathunter
```

You should see `com.flathunter.daily` in the output.

## Step 5: Test the Scheduled Job

Manually trigger a test run:

```bash
launchctl start com.flathunter.daily
```

Then check the logs:

```bash
# Create log directory if it doesn't exist
mkdir -p ~/.flathunter/logs

# View the latest log
ls -lt ~/.flathunter/logs/ | head -5
tail -100 ~/.flathunter/logs/flathunter_*.log
```

## That's It!

The app will now run automatically every night at 7:00 PM.

## View Logs Anytime

```bash
# See all log files
ls -lt ~/.flathunter/logs/

# Read the latest run
tail -100 $(ls -t ~/.flathunter/logs/flathunter_*.log | head -1)
```

## Troubleshooting

If something doesn't work, see the detailed `SCHEDULING.md` guide for more help.

## Stop the Scheduled Job

If you want to stop the automatic runs:

```bash
launchctl unload ~/Library/LaunchAgents/com.flathunter.daily.plist
```
