# Data Directory

This directory contains runtime data, database files, and output files.

## Files

- **processed_ids.db** - SQLite database tracking processed expose IDs
- **flathunter_results.json** - JSON output from file notifier (if enabled)

## Notes

- This directory is typically `.gitignore`d to avoid committing local data
- Database files are created automatically on first run
- The `database_location` config option determines where SQLite files are stored
- JSON output is only created when using the `file` notifier

## Database Schema

The SQLite database contains:
- `processed` - IDs of exposes already sent to users
- `exposes` - Full expose data with timestamps
- `executions` - Timestamps of crawler runs
- `users` - User settings (for web interface)

## Backup

To backup your processed IDs:
```bash
cp data/processed_ids.db data/processed_ids.db.backup
```

To reset (start receiving all listings again):
```bash
rm data/processed_ids.db
```
