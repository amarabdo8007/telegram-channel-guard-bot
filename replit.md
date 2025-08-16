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

### Deployment Configuration Updates (Latest)
- **Health Check Endpoints Verified**: Both `/` and `/health` endpoints returning proper JSON responses
- **Flask Server Integration**: Successfully running on port 5000 with proper HTTP responses
- **Dependencies**: Flask 3.1.1 installed and configured in pyproject.toml
- **Main Entry Point**: main.py properly configured as application entry point
- **Port Configuration**: Using PORT environment variable with fallback to 5000
- **Threading**: Flask server runs in daemon thread alongside Telegram bot polling