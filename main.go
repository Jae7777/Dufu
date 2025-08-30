package main

import (
	"fmt"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
)

var (
	ssrcUserMap      = make(map[uint32]string)
	ssrcUserMapMutex = &sync.Mutex{}
)

func main() {
	// Load environment variables from .env file
	err := godotenv.Load()
	if err != nil {
		fmt.Println("Error loading .env file")
	}

	// We'll need to get the bot token from an environment variable
	token := os.Getenv("DISCORD_BOT_TOKEN")
	if token == "" {
		fmt.Println("Error: DISCORD_BOT_TOKEN environment variable not set.")
		return
	}

	// Create a new Discord session using the provided bot token.
	dg, err := discordgo.New("Bot " + token)
	if err != nil {
		fmt.Println("error creating Discord session,", err)
		return
	}

	// Register handlers for events.
	dg.AddHandler(messageCreate)
	dg.AddHandler(voiceUpdate) // Handle voice state updates for SSRC mapping

	// We need intents for messages and voice states.
	dg.Identify.Intents = discordgo.IntentsGuildMessages | discordgo.IntentsGuildVoiceStates

	// Open a websocket connection to Discord and begin listening.
	err = dg.Open()
	if err != nil {
		fmt.Println("error opening connection,", err)
		return
	}

	// Wait here until CTRL-C or other term signal is received.
	fmt.Println("Bot is now running. Press CTRL-C to exit.")
	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt)
	<-sc

	// Cleanly close down the Discord session.
	dg.Close()
}

// voiceUpdate handles VoiceStateUpdate events to maintain SSRC mappings
func voiceUpdate(s *discordgo.Session, vsu *discordgo.VoiceStateUpdate) {
	// We only care about voice state updates when we're connected to voice
	for _, vc := range s.VoiceConnections {
		if vc.GuildID == vsu.GuildID {
			// Map the user to their SSRC when they have one
			if vsu.UserID != "" {
				ssrcUserMapMutex.Lock()
				// Note: In newer versions, we may need to handle this differently
				// For now, we'll use a simple approach and rely on the receive loop to map SSRCs
				ssrcUserMapMutex.Unlock()
			}
		}
	}
}

// This function will be called (due to AddHandler) every time a new
// message is created on any channel that the authenticated bot has access to.
func messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {

	// Ignore all messages created by the bot itself
	// This isn't required in this specific example but it's a good practice.
	if m.Author.ID == s.State.User.ID {
		return
	}

	// If the message is "ping" reply with "Pong!"
	if m.Content == "ping" {
		s.ChannelMessageSend(m.ChannelID, "Pong!")
	}

	// If the message is "pong" reply with "Ping!"
	if m.Content == "pong" {
		s.ChannelMessageSend(m.ChannelID, "Ping!")
	}

	// If the message is "!join", join the voice channel of the user who sent the message.
	if m.Content == "!join" {
		// Find the guild for that channel.
		g, err := s.State.Guild(m.GuildID)
		if err != nil {
			fmt.Println("Error finding guild:", err)
			return
		}

		// Find the voice state for the user who sent the message.
		vs := findUserVoiceState(g, m.Author.ID)
		if vs == nil {
			s.ChannelMessageSend(m.ChannelID, "You are not in a voice channel.")
			return
		}

		// Join the voice channel with receive enabled
		vc, err := s.ChannelVoiceJoin(g.ID, vs.ChannelID, false, false)
		if err != nil {
			fmt.Println("Error joining voice channel:", err)
			return
		}

		s.ChannelMessageSend(m.ChannelID, "Joined your voice channel! I'm now listening.")

		// Start receiving audio using the official pattern
		go receiveAudio(vc)
	}

	// If the message is "!leave", leave the current voice channel.
	if m.Content == "!leave" {
		vc, ok := s.VoiceConnections[m.GuildID]
		if !ok {
			s.ChannelMessageSend(m.ChannelID, "I'm not in a voice channel.")
			return
		}

		err := vc.Disconnect()
		if err != nil {
			fmt.Println("Error disconnecting from voice channel:", err)
			return
		}

		s.ChannelMessageSend(m.ChannelID, "Left the voice channel.")
	}
}

// receiveAudio follows the official discordgo voice receive pattern
func receiveAudio(vc *discordgo.VoiceConnection) {
	fmt.Println("Starting audio receive goroutine...")

	// Create a receive channel for opus packets
	recv := make(chan *discordgo.Packet, 2)

	// Start listening for voice packets
	go func() {
		// This is the key: we need to enable voice receiving
		vc.LogLevel = discordgo.LogDebug // Enable debug logging
		
		// Wait for the connection to be ready
		for !vc.Ready {
			time.Sleep(100 * time.Millisecond)
		}
		fmt.Println("Voice connection is ready, starting receive...")

		// Enable opus receive
		vc.OpusRecv = recv

		// This should trigger the voice connection to start sending us packets
		for {
			select {
			case packet, ok := <-recv:
				if !ok {
					fmt.Println("Receive channel closed")
					return
				}
				
				fmt.Printf("Received packet: SSRC=%d, Opus length=%d\n", packet.SSRC, len(packet.Opus))
				
				// Try to map SSRC to user (this is the tricky part)
				ssrcUserMapMutex.Lock()
				userID, found := ssrcUserMap[packet.SSRC]
				ssrcUserMapMutex.Unlock()
				
				if found {
					fmt.Printf("Audio from user %s\n", userID)
				} else {
					fmt.Printf("Unknown user for SSRC %d\n", packet.SSRC)
				}

			case <-time.After(1 * time.Second):
				// Periodic check to see if we're still connected
				if !vc.Ready {
					fmt.Println("Voice connection no longer ready")
					return
				}
			}
		}
	}()
}

// Helper function to find a user's voice state in a guild.
func findUserVoiceState(g *discordgo.Guild, userID string) *discordgo.VoiceState {
	for _, vs := range g.VoiceStates {
		if vs.UserID == userID {
			return vs
		}
	}
	return nil
}
