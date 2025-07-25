# Real Estate Management System

## Overview

This is a comprehensive real estate management system that automates property data processing through integration with multiple external services. The system receives property listings from Telegram, processes them using AI, stores data in both Notion and Zoho CRM, and provides a web interface for monitoring and management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: FastAPI for web interface and API endpoints
- **Language**: Python 3.x with async/await patterns
- **Database**: SQLite for local data storage and caching
- **AI Processing**: Anthropic Claude API for natural language processing
- **External Integrations**: Telegram Bot API, Notion API, Zoho CRM API

### Frontend Architecture
- **Framework**: Bootstrap 5 with RTL (Right-to-Left) support for Arabic
- **JavaScript**: Vanilla JavaScript with async operations
- **Styling**: Custom CSS with Arabic language support
- **Templates**: Jinja2 templating engine

### Data Processing Pipeline
1. **Input**: Telegram channel messages containing property listings
2. **AI Processing**: Claude AI extracts structured data from Arabic text
3. **Classification**: Properties are categorized as "new", "duplicate", or "multiple"
4. **Storage**: Data is stored in Notion (properties and owners) and Zoho CRM
5. **Notification**: Results are sent back to Telegram bot

## Key Components

### Core Services
- **AIService**: Handles property data extraction from Arabic text using Anthropic Claude
- **NotionService**: Manages property and owner data in Notion databases
- **TelegramService**: Handles message retrieval and notification sending
- **ZohoService**: Syncs property data with Zoho CRM system
- **DatabaseManager**: Local SQLite database for caching and system state

### Property Classification Logic
- **New Property**: No matching records found
- **Duplicate Property**: Exact match on owner phone, region, property type, condition, area, and floor
- **Multiple Property**: Same owner phone number but different property details

### Data Models
- **PropertyData**: Comprehensive property information structure
- **PropertyStatus**: Enumeration of property processing states
- **Property Enums**: Standardized values for availability, condition, and type

## Data Flow

1. **Message Ingestion**: System monitors Telegram channel for new property listings
2. **AI Processing**: Raw Arabic text is sent to Claude API for structured data extraction
3. **Duplicate Detection**: System searches Notion for existing properties using matching criteria
4. **Data Storage**: 
   - Property details stored in Notion Properties database
   - Owner information stored in Notion Owners database
   - Complete record synced to Zoho CRM
5. **Notification**: Classification result sent to Telegram bot with relevant links

## External Dependencies

### Required APIs
- **Telegram Bot API**: For message monitoring and notifications
- **Notion API**: For property and owner data management
- **Anthropic Claude API**: For AI-powered text processing
- **Zoho CRM API**: For customer relationship management integration

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Bot authentication token
- `TELEGRAM_CHANNEL_ID`: Target channel identifier
- `NOTION_INTEGRATION_SECRET`: Notion workspace integration token
- `NOTION_PROPERTIES_DB_ID`: Properties database identifier
- `NOTION_OWNERS_DB_ID`: Owners database identifier
- `ANTHROPIC_API_KEY`: Claude AI API key
- `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`: CRM authentication

## Deployment Strategy

### Local Development
- SQLite database for development and testing
- Environment variables loaded from `.env` file
- FastAPI development server with hot reload

### Production Considerations
- Web interface runs on FastAPI with uvicorn server
- Background processing for Telegram message monitoring
- Logging system with file and console output
- Error handling and retry mechanisms for external API calls
- Configuration management through environment variables

### System Requirements
- Python 3.8+ with asyncio support
- Network access for external API integrations
- Persistent storage for SQLite database
- Memory for AI processing operations

The system is designed as a long-running service that continuously monitors Telegram channels, processes property data, and maintains synchronization across multiple platforms while providing real-time status through a web dashboard.