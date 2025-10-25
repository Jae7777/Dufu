# Discord Voice AI Bot Setup Guide

## Overview
This Discord bot joins voice channels, listens to speech, transcribes it using OpenAI Whisper, and generates intelligent responses using GPT.

## Features
- 🎙️ Real-time speech-to-text using OpenAI Whisper
- 🤖 AI-powered responses using GPT-3.5/4
- 💬 Conversation history tracking
- 🎯 Smart voice activity detection
- 📊 Status monitoring and management

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

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
Use this URL template to invite your bot:
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

## Technical Details

### Audio Processing
- Receives voice packets from Discord (48kHz stereo PCM)
- Converts to suitable format for STT services
- Handles voice activity detection and silence removal
- Buffers audio for optimal transcription accuracy

### Speech Recognition

#### OpenAI Whisper:
- File-based transcription with high accuracy
- Optimized for natural conversations
- Costs ~$0.006 per minute of audio
- Handles various accents and languages

### Response Generation
- Uses OpenAI GPT-3.5-turbo by default
- Maintains conversation context (last 10 messages)
- Optimized prompts for voice conversations
- Keeps responses brief and natural

### Text-to-Speech
- **Note**: TTS has been removed for simplicity
- Bot responses are logged to console and stored in conversation history
- Can be easily re-added with external TTS services if needed

## Configuration Options

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_TOKEN` | Yes | Discord bot token |
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT and Whisper |
| `AZURE_SPEECH_KEY` | No | Azure Speech service key |
| `AZURE_SPEECH_REGION` | No | Azure region (e.g., eastus) |

### Customization

#### Change AI Model:
In `bot.py`, modify the OpenAI call:
```python
model="gpt-4"  # or gpt-3.5-turbo-16k
```

#### Change TTS Voice:
In `bot.py`, modify the speech config:
```python
speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
```

Available voices: JennyNeural, AriaNeural, GuyNeural, etc.

#### Adjust Conversation Memory:
```python
conversation_history = defaultdict(lambda: deque(maxlen=100))  # Increase from 50
```

## Troubleshooting

### Common Issues

#### "Import could not be resolved" errors:
- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- You may need to install additional system packages for audio processing

#### Bot can't connect to voice channel:
- Check bot permissions (Connect + Speak)
- Verify the bot is in the same server
- Check if voice channel has user limits

#### No audio transcription:
- Verify your microphone is working in Discord
- Check if Azure Speech keys are correct
- Ensure OpenAI API key has Whisper access

#### TTS not working:
- Check Azure Speech TTS quota
- Verify speech synthesis permissions
- Check bot has Speak permission in voice channel

### Performance Tips

1. **Use Azure Speech**: Much faster than Whisper for real-time conversations
2. **Optimize conversation history**: Reduce `maxlen` for faster response generation
3. **Monitor API usage**: Both OpenAI and Azure charge per usage
4. **Voice Activity Detection**: The bot automatically filters silence

### Logs and Debugging

The bot provides detailed console logging:
- Connection status
- Audio processing events  
- Transcription results
- Response generation
- TTS playback status

Enable debug mode by adding print statements or using Python's logging module.

## Cost Estimation

### Typical 1-hour voice session:
- **Azure STT**: ~$1.00 (60 minutes)
- **OpenAI GPT**: ~$0.10 (100 responses)
- **Azure TTS**: ~$0.16 (100 responses)
- **OpenAI Whisper** (if used): ~$0.36 (60 minutes)

**Total**: ~$1.26/hour with Azure, ~$0.46/hour with Whisper only

## Security Notes

- Keep your `.env` file private (never commit to git)
- Regenerate API keys if compromised
- Monitor API usage for unexpected charges
- Consider rate limiting for production use

## Support

For issues and questions:
1. Check the console logs for error details
2. Verify all API keys are correct and have proper permissions
3. Test with simple commands first (`/status`, `/vc`)
4. Check Discord and API service status pages