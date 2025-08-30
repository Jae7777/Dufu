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
	// Removed invalid global speaking handler; we consume speaking updates from the voice connection.

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

		// Join the voice channel. Do NOT self-deafen so we can receive audio.
		vc, err := s.ChannelVoiceJoin(g.ID, vs.ChannelID, false, false)
		if err != nil {
			fmt.Println("Error joining voice channel:", err)
			return
		}

		// IMPORTANT: initialize the OpusRecv channel to enable receiving.
		vc.OpusRecv = make(chan *discordgo.Packet, 1024)

		s.ChannelMessageSend(m.ChannelID, "Joined your voice channel! I'm now listening.")

		// Wait for voice connection readiness (poll Ready bool up to 5 seconds).
		fmt.Println("Waiting for voice connection to be ready...")
		for i := 0; i < 50 && !vc.Ready; i++ {
			time.Sleep(100 * time.Millisecond)
		}
		if vc.Ready {
			fmt.Println("Voice connection ready. Starting receive loop...")
		} else {
			fmt.Println("Voice connection not signaled ready after 5s; attempting receive anyway...")
		}

		// Start a goroutine to listen for incoming audio packets.
		go func(vc *discordgo.VoiceConnection) {
			for {
				packet, ok := <-vc.OpusRecv
				if !ok {
					fmt.Println("Voice channel closed.")
					return
				}

				ssrc := packet.SSRC
				ssrcUserMapMutex.Lock()
				userID, userFound := ssrcUserMap[ssrc]
				ssrcUserMapMutex.Unlock()

				if userFound {
					fmt.Printf("Received audio: ssrc=%d user=%s bytes=%d\n", ssrc, userID, len(packet.Opus))
				} else {
					fmt.Printf("Received audio: ssrc=%d (user unknown yet) bytes=%d\n", ssrc, len(packet.Opus))
				}
			}
		}(vc)
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

// Helper function to find a user's voice state in a guild.
func findUserVoiceState(g *discordgo.Guild, userID string) *discordgo.VoiceState {
	for _, vs := range g.VoiceStates {
		if vs.UserID == userID {
			return vs
		}
	}
	return nil
}
