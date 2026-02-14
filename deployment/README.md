# Deployment Configuration

This directory contains all deployment-related configuration files.

## Files

- **Dockerfile** - Standard Docker image for local/cloud deployment
- **Dockerfile.gcloud.job** - Specialized Docker image for Google Cloud Run Jobs (includes Chrome/Selenium)
- **docker-compose.yaml** - Docker Compose configuration for local development
- **app.yaml** - Google App Engine deployment configuration
- **cloudbuild.yaml** - Google Cloud Build configuration
- **cron.yaml** - Google App Engine cron job configuration
- **sample-flathunter.service** - Systemd service file for Linux installations

## Usage

### Docker Compose
```bash
cd deployment
docker-compose up
```

### Docker
```bash
cd deployment
docker build -t flathunter -f Dockerfile ..
docker run --mount type=bind,source=$PWD/../config.yaml,target=/config.yaml flathunter
```

### Google Cloud
```bash
# From project root
gcloud app deploy deployment/app.yaml
gcloud app deploy deployment/cron.yaml
```

### Linux Service
```bash
sudo cp deployment/sample-flathunter.service /lib/systemd/system/flathunter.service
sudo systemctl enable flathunter --now
```
