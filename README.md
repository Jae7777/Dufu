Discord Voice AI Bot Setup Guide

## Overview
This Discord bot joins voice channels, listens to speech, transcribes it using OpenAI Whisper, and generates intelligent responses using GPT.

## Features
- Real-time speech-to-text using OpenAI Whisper
- AI-powered responses using GPT-3.5/4
- Conversation history tracking
- Smart voice activity detection
- Status monitoring and management

## Installation

1. Create a Virtual Environment:
python3 -m venv venv

Activate on Windows:
venv\Scripts\activate

Activate on macOS/Linux:
source venv/bin/activate

2. Install Dependencies:
pip install -r requirements.txt

3. Set Up Environment Variables:
Copy .env.example to .env and fill in your API keys.

4. Configure Your Bot:

Discord Setup:
- Go to Discord Developer Portal
- Create a new application
- Create a bot and copy the token
- Enable Message Content Intent and optionally Server Members Intent

Set the Bot Permissions:
- Connect
- Speak
- Use Slash Commands
- Send Messages

Invite URL template:
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=3146752&scope=bot%20applications.commands

5. API Services Setup:
OpenAI (Required):
- Generate an API key
- Add OPENAI_API_KEY to .env

## Usage

Commands:
/vc - Join voice channel
/leave - Leave
/history - View conversation history
/status - Check bot status

Voice Interaction Flow:
1. Join with /vc
2. Speak
3. Bot transcribes and responds
4. Continue conversation
5. Use /leave to disconnect

## Technical Details

Audio Processing:
- Receives PCM 48kHz audio
- Converts for STT
- Voice activity detection
- Silence removal

Speech Recognition:
Whisper features, cost, language support.

Response Generation:
GPT models, brief responses, context memory.

Text-to-Speech:
Removed for simplicity;

## Troubleshooting

Common Issues:
- Missing imports: reinstall requirements
- Bot can't connect: check permissions
- No transcription: check mic + API keys

Performance Tips:
- Reduce conversation history
- Monitor API usage

Logs:
Debug output in console.
