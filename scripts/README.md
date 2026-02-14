# Scripts and Development Tools

This directory contains development scripts, debugging tools, and utilities.

## Files

### Configuration
- **config_wizard.py** - Interactive wizard to generate config.yaml
- **config_wizard_test.py** - Tests for the config wizard

### Development Tools
- **chrome_driver_install.py** - Helper script to install Chrome WebDriver
- **cloud_job.py** - Utility for running flathunter as a cloud job

### Debug Scripts
- **debug_zoopla.py** - Debugging script for Zoopla crawler
- **zoopla_debug.html** - HTML output from Zoopla debugging (if present)

### Build Tools
- **pleasew** - Please build tool wrapper
- **.plzconfig** - Please build tool configuration
- **plugins/** - Please build tool plugins

## Usage

### Run Configuration Wizard
```bash
python scripts/config_wizard.py
```

### Debug a Crawler
```bash
python scripts/debug_zoopla.py
```

### Install Chrome Driver
```bash
python scripts/chrome_driver_install.py
```
