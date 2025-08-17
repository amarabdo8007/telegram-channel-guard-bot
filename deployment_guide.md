# Deployment Guide

## Quick Start
This Telegram bot application is ready for deployment on Replit Autoscale. All necessary configurations are in place.

## Deployment Configuration Files

### 1. Main Entry Point
- **File**: `server.py`
- **Purpose**: Deployment-optimized entry point that runs both HTTP server and Telegram bot
- **Architecture**: Flask HTTP server in background thread, Telegram bot in main thread

### 2. Configuration Files
- `replit.toml` - Replit-specific deployment configuration
- `app.yaml` - Google App Engine style configuration
- `Procfile` - Heroku-style process configuration
- `pyproject.toml` - Python dependencies and project metadata

### 3. Health Check Endpoints
All endpoints return proper HTTP status codes and JSON responses:

- `GET /` - Primary health check endpoint
  ```json
  {
    "status": "healthy",
    "service": "telegram-bot", 
    "message": "Bot is running",
    "bot_initialized": true,
    "timestamp": "repl-id",
    "port": "5000"
  }
  ```

- `GET /health` - Simple health check
  ```json
  {"status": "ok"}
  ```

- `GET /ping` - Basic connectivity test
  ```text
  pong
  ```

- `GET /bot-status` - Detailed bot status
  ```json
  {
    "status": "active",
    "bot": "running",
    "handlers": "loaded", 
    "application_running": true
  }
  ```

## Deployment Steps

1. **Environment Variables**: Ensure `TELEGRAM_BOT_TOKEN` is set in Replit Secrets
2. **Run Command**: When deploying, set the run command to: `python3 server.py`
3. **Deploy**: Click the Deploy button in Replit  
4. **Verify**: Check health endpoints after deployment

## Manual Run Command Configuration

If the deployment shows "Run command cannot be empty", set the run command in the deployment UI to one of:
- `python3 server.py` (recommended)
- `python3 start.py` (alternative)
- `python3 main.py` (legacy option)

## Troubleshooting

### Common Issues
- **Health check failures**: Verify port 5000 is accessible and Flask server is running
- **Bot not responding**: Check TELEGRAM_BOT_TOKEN is correctly set in secrets
- **Entry point errors**: Ensure `server.py` is specified as the main file

### Deployment Logs
Monitor the console logs for:
- "Starting HTTP server on 0.0.0.0:5000"
- "Telegram bot is starting..."
- "Application started"

## Architecture Benefits
- ✅ HTTP server for health checks (required for Autoscale)
- ✅ Telegram bot runs in main thread (proper signal handling)
- ✅ Background threading prevents blocking
- ✅ Multiple health endpoints for different monitoring needs
- ✅ Proper error handling and status reporting
- ✅ Port configuration from environment variables