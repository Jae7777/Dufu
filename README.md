Discord Voice AI Bot Setup Guide

## Overview
This Discord bot joins voice channels, listens to speech, transcribes it using OpenAI Whisper, and generates intelligent responses using GPT.

## Features
- Real-time speech-to-text using OpenAI Whisper
- AI-powered responses using GPT-3.5/4
- Conversation history tracking
- Smart voice activity detection
- Status monitoring and management

## 1. Installation

1. Create a Virtual Environment:
python3 -m venv venv

Activate on Windows:
venv\Scripts\activate

Activate on macOS/Linux:
source venv/bin/activate

2. Install FFmpeg (Required)

FFmpeg is required for audio processing.

Windows:  
Download from https://www.gyan.dev/ffmpeg/builds/  
Add the `bin` folder to PATH.

3. Install Dependencies:
pip install -r requirements.txt

### 2. Set Up Environment Variables
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

### 3. Configure Your Bot

#### Discord Setup:
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section
4. Create a bot and copy the token
5. **IMPORTANT**: Enable these privileged intents:
   - ✅ **Message Content Intent** (Required for voice commands)
   - ✅ **Server Members Intent** (Optional, for better user detection)

#### Bot Permissions:
Your bot needs these permissions in Discord servers:
- Connect (to join voice channels)
- Speak (to play TTS audio)  
- Use Slash Commands
- Send Messages

#### Invite URL:
Use this URL template to invite your bot to a discord server:
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=3146752&scope=bot%20applications.commands
```

### 4. API Services Setup

#### OpenAI (Required):
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an API key
3. Add to `.env` as `OPENAI_API_KEY`

**Note:** This bot uses OpenAI Whisper for speech-to-text and GPT for conversation responses.

## Usage

### Commands

- `/vc` - Join your voice channel and start listening
- `/leave` - Leave voice channel and save conversation
- `/history` - View recent conversation history  
- `/status` - Check bot connection status

### Voice Interaction Flow

1. **Join**: Use `/vc` while in a voice channel
2. **Speak**: Talk naturally - the bot listens for speech
3. **AI Response**: Bot transcribes, generates response, and speaks back
4. **Continue**: Have natural conversations
5. **Leave**: Use `/leave` to disconnect and save history


