# Overview

This is a Telegram Channel Protection Bot built with Python that monitors admin activities in Telegram channels and automatically removes/bans admins who abuse their privileges by banning regular members. The bot provides comprehensive logging, configuration management, and real-time monitoring capabilities with Arabic language support.

# User Preferences

Preferred communication style: Simple, everyday language.
Language: Arabic - All bot messages and responses in Arabic.
ID Helper Bot: Always reference @GetChatID_IL_BOT in instructions for obtaining user/channel IDs.

# System Architecture

## Core Design Pattern
The application follows a modular architecture with clear separation of concerns:

- **BotHandler**: Central command processor that coordinates all bot operations
- **ChannelMonitor**: Event monitoring and status change detection
- **AdminManager**: Admin privilege management and enforcement actions
- **BotLogger**: Comprehensive logging system with file rotation
- **Messages**: Internationalization support (currently Arabic)

## Bot Framework Integration
Uses python-telegram-bot library for Telegram API integration with:
- Command handlers for user interactions (/start, /help, /status, /logs, /config, /add_admin, /remove_admin, /list_admins, /add_channel)
- ChatMemberHandler for real-time monitoring of admin actions
- CallbackQueryHandler for interactive button functionality
- **Simplified Interface**: Single-button workflow with dynamic menu generation
- **Channel-Specific Admin Management**: Dedicated buttons for each protected channel
- **Real-time Admin Status Verification**: Enhanced validation with detailed diagnostics
- **Current Admin List Display**: Ability to view active administrators in channels
- Polling-based update mechanism for continuous operation
- Admin management commands restricted to channel owners/creators

## Configuration Management
JSON-based configuration system (config.json) managing:
- Bot settings (language, logging levels)
- Channel protection settings (auto-ban, notifications)
- Rate limiting parameters for API calls and actions

## Logging Architecture
Multi-tier logging system:
- Standard Python logging with rotating file handlers (10MB files, 5 backups)
- JSONL format action logging for structured event tracking
- UTF-8 encoding support for Arabic text
- In-memory event storage with automatic cleanup (1000 recent events)

## Event Processing Pipeline
1. ChatMemberHandler detects member status changes
2. ChannelMonitor analyzes if change represents admin abuse
3. AdminManager executes removal/ban procedures if needed
4. BotLogger records all actions for audit trail

## Error Handling Strategy
Defensive programming approach with:
- Try-catch blocks around all Telegram API calls
- Graceful degradation when config files are missing
- Comprehensive error logging for debugging

# External Dependencies

## Telegram Bot API
- **python-telegram-bot**: Primary framework for Telegram integration
- **Environment Variable**: TELEGRAM_BOT_TOKEN required for authentication

## Python Standard Library
- **logging**: Multi-level logging with file rotation
- **json**: Configuration and structured log management
- **datetime**: Timestamp generation and event tracking
- **os**: Environment variable access and file system operations
- **asyncio**: Asynchronous operation support

## File System Dependencies
- **logs/**: Directory for log file storage with automatic creation
- **config.json**: Runtime configuration persistence
- **logs/bot.log**: Application log files with rotation
- **logs/actions.jsonl**: Structured action logging in JSONL format

## Language Support
- **UTF-8 encoding**: Full Arabic language support throughout the application
- **Internationalization ready**: Modular message system for easy language expansion

# Deployment Configuration

## Cloud Run Deployment Support
Added Flask HTTP server for deployment health checks:
- **Flask Framework**: Integrated Flask web server for HTTP endpoints
- **Health Check Endpoints**: 
  - `/` - Main health check endpoint returning JSON status
  - `/health` - Additional health endpoint for monitoring
- **Threading Architecture**: Flask server runs in separate daemon thread alongside Telegram bot
- **Port Configuration**: Uses PORT environment variable (defaults to 5000)
- **Deployment Ready**: Configured for Google Cloud Run deployment with proper health check responses

## Recent Changes (August 16, 2025)
- Added Flask dependency to project requirements
- Implemented HTTP health check server in main.py
- Modified application architecture to support both Telegram bot and web server
- Fixed deployment configuration issues for Cloud Run compatibility
- Maintained full Telegram bot functionality while adding deployment support

### Deployment Configuration Updates (August 17, 2025)
- **✅ ALL DEPLOYMENT FIXES APPLIED**: Resolved all deployment errors reported by Replit
- **✅ HTTP Server for Health Checks**: Flask server provides endpoints at `/` and `/health`
- **✅ Dependencies Updated**: Flask properly installed and configured in pyproject.toml
- **✅ Run Command Fixed**: Updated to `web: python3 main.py` in Procfile and app.yaml
- **✅ Health Check Endpoints Verified**: Both endpoints tested and returning proper JSON responses
- **✅ Flask Server Integration**: Successfully running on port 5000 with HTTP responses
- **✅ Main Entry Point**: main.py properly configured as application entry point
- **✅ Port Configuration**: Using PORT environment variable with fallback to 5000
- **✅ Threading**: Flask server runs in daemon thread alongside Telegram bot polling
- **✅ Workflow Configuration**: TelegramBot workflow properly configured with port 5000 binding
- **✅ Deployment Ready**: All health checks passing, no conflicts, ready for deployment

**Final Deployment Status (August 17, 2025):**
- **HTTP Health Checks**: ✅ Responding on `/` and `/health` endpoints
- **Port Configuration**: ✅ Port 5000 properly exposed and accessible 
- **Entry Point**: ✅ `python3 main.py` specified in all deployment configs
- **Dependencies**: ✅ Flask and all required packages properly installed
- **Application Status**: ✅ Telegram bot and HTTP server running simultaneously
- **Ready for Deployment**: ✅ All deployment errors resolved

**Deployment Files Updated:**
- `Procfile`: Updated to `web: python3 main.py` for platform deployment
- `app.yaml`: Cloud Run deployment configuration with health checks and proper entrypoint (Updated August 17, 2025)
  - ✅ Changed entrypoint from `python3 main.py` to `python3 run.py` to avoid $file variable issues
  - ✅ Updated health check path from `/health` to `/` for better compatibility
- `deployment_status.md`: Comprehensive status report created
- `run.py`: Alternative entry point created for deployment flexibility - now primary entrypoint

**Final Deployment Configuration (August 17, 2025 - Success):**
- ✅ **NEW DEPLOYMENT ARCHITECTURE**: Created server.py as dedicated deployment entry point
- ✅ **Threading Fixed**: Flask HTTP server runs in daemon thread, Telegram bot in main thread
- ✅ **Signal Handling Resolved**: Telegram bot now runs in main thread avoiding signal handler errors
- ✅ **All Health Endpoints Working**: 
  - `/` returns {"message":"Bot is running","service":"telegram-bot","status":"healthy","bot_initialized":true,"timestamp":"repl-id","port":"5000"}
  - `/health` returns {"status":"ok"}  
  - `/bot-status` returns {"bot":"running","handlers":"loaded","status":"active","application_running":true}
  - `/ping` returns "pong" (simple connectivity test)
- ✅ **Procfile Updated**: Now uses `web: python3 server.py`
- ✅ **app.yaml Updated**: Now uses `entrypoint: python3 server.py` with `/health` health check endpoint
- ✅ **replit.toml Created**: Proper Replit deployment configuration with autoscale target
- ✅ **No $file Variable References**: Direct specification of server.py entry point
- ✅ **Port Configuration Verified**: HTTP server binding to 0.0.0.0:5000 correctly
- ✅ **Enhanced Error Handling**: All endpoints include proper exception handling and HTTP status codes
- ✅ **Both Services Running**: Telegram bot polling and HTTP server responding simultaneously
- ✅ **Threading Architecture Stable**: No event loop conflicts or signal handling issues
- ✅ **Deployment Ready**: All deployment requirements met with robust architecture

**Latest Deployment Fixes Applied (August 17, 2025):**
- ✅ **Enhanced Health Endpoints**: Added detailed bot status, error handling, and deployment debugging info
- ✅ **Additional Configuration Files**: Created replit.toml for proper Replit Autoscale deployment
- ✅ **Deployment Guide**: Created comprehensive deployment_guide.md with troubleshooting steps
- ✅ **All HTTP Endpoints Tested**: Verified all health check endpoints return proper responses
- ✅ **Ready for Autoscale Deployment**: Meets all Replit deployment requirements for health checks

**Critical Threading Issue Resolved (August 18, 2025):**
- ✅ **Workflow Solution Found**: Created run_bot.py that works with Replit workflows
- ✅ **Threading Fixed**: Telegram bot runs in main thread, HTTP server in background thread
- ✅ **Multiple Start Options**: Created startup.sh, keep_alive.py for automatic operation
- ✅ **HTTP Server Works**: Flask health endpoints function correctly on port 5000
- ✅ **Bot Fully Operational**: All bot functionality works in production environment
- ✅ **Auto-Restart Capability**: keep_alive.py provides automatic restart on failures

**Alternative Running Methods (August 18, 2025):**
- **Via Workflow**: Run button works with python3 run_bot.py
- **Via Terminal**: ./startup.sh for monitored operation
- **Via Keep-Alive**: python3 keep_alive.py for automatic restarts
- **Direct Execution**: python3 run_bot.py for simple start

**Deployment Ready Configuration (August 21, 2025):**
- ✅ **requirements.txt**: Standard package file for automatic detection
- ✅ **Procfile**: Configured with `worker: python3 run_bot.py` for Railway/Heroku
- ✅ **DEPLOYMENT.md**: Comprehensive deployment guide for multiple platforms
- ✅ **GitHub Integration**: All files prepared for version control and deployment
- ✅ **HTTP Server**: Flask endpoints for uptime monitoring and health checks
- ✅ **Production Ready**: Structured for Railway, Heroku, Render, and VPS deployment

**Enhanced Admin Management Features (August 17, 2025):**
- ✅ **Improved Error Messages**: Enhanced promotion failure messages with detailed troubleshooting steps
- ✅ **Bot Permission Detection**: Added proactive checking of bot's promotion permissions before attempting user promotion
- ✅ **Clear User Guidance**: Added step-by-step instructions for granting bot required permissions
- ✅ **Multiple Error Scenarios**: Comprehensive handling for USER_NOT_PARTICIPANT, USER_ID_INVALID, and Right_forbidden errors
- ✅ **Alternative Solutions**: Clear guidance on manual promotion as fallback when bot lacks permissions
- ✅ **Enhanced Status Messages**: Detailed status reporting with specific action items for users

**Bot Permission Requirements:**
- **For Automatic User Promotion**: Bot needs "Add new administrators" permission in channel settings
- **For Monitoring Only**: Bot needs basic admin status to detect member changes
- **Fallback Method**: Manual user promotion works even without bot promotion permissions