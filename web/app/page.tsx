export default function Home() {
  // TODO: Replace this with your actual bot invite link from Discord Developer Portal
  // Go to: Discord Developer Portal > Your App > OAuth2 > URL Generator
  // Select: bot scope, then Connect, Speak, Send Messages permissions
  const BOT_INVITE_LINK = "https://discord.com/oauth2/authorize?client_id=1411401721225281566";

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-slate-900 dark:text-white mb-4">
            🎙️ Dufu Voice Transcription Bot
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-300 mb-8">
            Record and transcribe voice conversations in your Discord server
          </p>
          
          {/* Main CTA */}
          <a
            href={BOT_INVITE_LINK}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-lg px-8 py-4 rounded-lg shadow-lg transition-all transform hover:scale-105"
          >
            ✨ Add to Discord
          </a>
        </header>

        {/* Main Content */}
        <main className="space-y-8">
          {/* Features Section */}
          <section className="bg-white dark:bg-slate-800 rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
              Why Use Dufu?
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="flex items-start space-x-3">
                <span className="text-2xl">🎙️</span>
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">Voice Recording</h3>
                  <p className="text-slate-600 dark:text-slate-400 text-sm">
                    Automatically records all participants in your voice channel
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-2xl">📝</span>
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">Live Transcription</h3>
                  <p className="text-slate-600 dark:text-slate-400 text-sm">
                    Converts speech to text using Google Speech Recognition
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-2xl">💾</span>
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">Audio Files</h3>
                  <p className="text-slate-600 dark:text-slate-400 text-sm">
                    Saves recordings as high-quality WAV files
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-2xl">⚡</span>
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">Easy to Use</h3>
                  <p className="text-slate-600 dark:text-slate-400 text-sm">
                    Simple slash commands - no setup required
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Quick Start */}
          <section className="bg-white dark:bg-slate-800 rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">
              🚀 Quick Start Guide
            </h2>

            <div className="space-y-6">
              {/* Step 1 */}
              <div className="flex items-start space-x-4">
                <span className="flex-shrink-0 bg-indigo-500 text-white rounded-full w-10 h-10 flex items-center justify-center font-bold">
                  1
                </span>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                    Invite the Bot
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400 mb-3">
                    Click the "Add to Discord" button above and select your server. You'll need{" "}
                    <strong>Manage Server</strong> permission.
                  </p>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex items-start space-x-4">
                <span className="flex-shrink-0 bg-indigo-500 text-white rounded-full w-10 h-10 flex items-center justify-center font-bold">
                  2
                </span>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                    Join a Voice Channel
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400">
                    Connect to any voice channel in your server where you want to record.
                  </p>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex items-start space-x-4">
                <span className="flex-shrink-0 bg-indigo-500 text-white rounded-full w-10 h-10 flex items-center justify-center font-bold">
                  3
                </span>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                    Start Recording
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400 mb-2">
                    Type <code className="bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded text-sm font-mono">/record</code> in any text channel.
                  </p>
                  <p className="text-slate-600 dark:text-slate-400">
                    The bot will join your voice channel and start recording! 🎙️
                  </p>
                </div>
              </div>

              {/* Step 4 */}
              <div className="flex items-start space-x-4">
                <span className="flex-shrink-0 bg-indigo-500 text-white rounded-full w-10 h-10 flex items-center justify-center font-bold">
                  4
                </span>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                    Stop Recording
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400 mb-2">
                    When you're done, type <code className="bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded text-sm font-mono">/stop</code>
                  </p>
                  <p className="text-slate-600 dark:text-slate-400">
                    The bot will process and save the audio, then leave the channel.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Commands Section */}
          <section className="bg-white dark:bg-slate-800 rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
              📋 Commands
            </h2>
            <div className="space-y-4">
              <div className="border-l-4 border-indigo-500 pl-4">
                <div className="flex items-center space-x-2 mb-2">
                  <code className="bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 px-3 py-1 rounded font-mono text-sm font-semibold">
                    /record
                  </code>
                </div>
                <p className="text-slate-700 dark:text-slate-300">
                  Joins your current voice channel and starts recording audio from all participants.
                  You must be in a voice channel to use this command.
                </p>
              </div>
              
              <div className="border-l-4 border-indigo-500 pl-4">
                <div className="flex items-center space-x-2 mb-2">
                  <code className="bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 px-3 py-1 rounded font-mono text-sm font-semibold">
                    /stop
                  </code>
                </div>
                <p className="text-slate-700 dark:text-slate-300">
                  Stops the recording, processes the audio files, and makes the bot leave the voice channel.
                  Transcriptions (if enabled) will be posted in the channel.
                </p>
              </div>
            </div>
          </section>

          {/* FAQ */}
          <section className="bg-white dark:bg-slate-800 rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
              ❓ Frequently Asked Questions
            </h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white mb-2">
                  Who can use the bot's commands?
                </h3>
                <p className="text-slate-600 dark:text-slate-400">
                  Any member with permission to use slash commands in your server can control the bot.
                  Make sure to set appropriate role permissions if you want to restrict access.
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white mb-2">
                  Where are the recordings saved?
                </h3>
                <p className="text-slate-600 dark:text-slate-400">
                  Audio files are saved on the bot's server. Transcriptions are posted directly in your Discord channel.
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white mb-2">
                  Can the bot record multiple channels at once?
                </h3>
                <p className="text-slate-600 dark:text-slate-400">
                  Currently, the bot can only record one voice channel per server at a time.
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white mb-2">
                  Is this bot free to use?
                </h3>
                <p className="text-slate-600 dark:text-slate-400">
                  Yes! This bot is completely free to use in your Discord server.
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white mb-2">
                  The bot isn't responding to commands. What should I do?
                </h3>
                <p className="text-slate-600 dark:text-slate-400">
                  Make sure the bot has the necessary permissions (Connect, Speak, Send Messages) and that it's online.
                  If issues persist, try kicking and re-inviting the bot to your server.
                </p>
              </div>
            </div>
          </section>

          {/* Privacy Notice */}
          <section className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-6">
            <h2 className="text-xl font-bold text-amber-900 dark:text-amber-200 mb-3 flex items-center">
              <span className="mr-2">🔒</span>
              Privacy & Usage Notice
            </h2>
            <p className="text-amber-800 dark:text-amber-300 text-sm">
              This bot records audio from voice channels. Please ensure all participants are aware they are being recorded
              and have consented. It is your responsibility to comply with local recording and privacy laws. The bot operators
              are not responsible for how you use this service.
            </p>
          </section>

          {/* Support */}
          <section className="bg-white dark:bg-slate-800 rounded-lg shadow-md p-6 text-center">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">
              Need Help?
            </h2>
            <p className="text-slate-600 dark:text-slate-400 mb-4">
              If you're experiencing issues or have questions, feel free to reach out!
            </p>
            <div className="flex justify-center space-x-4">
              <a
                href="https://github.com/yourusername/dufu"
                target="_blank"
                rel="noopener noreferrer"
                className="text-indigo-600 dark:text-indigo-400 hover:underline font-medium"
              >
                📖 Documentation
              </a>
              <span className="text-slate-300 dark:text-slate-600">•</span>
              <a
                href="https://github.com/yourusername/dufu/issues"
                target="_blank"
                rel="noopener noreferrer"
                className="text-indigo-600 dark:text-indigo-400 hover:underline font-medium"
              >
                🐛 Report an Issue
              </a>
            </div>
          </section>
        </main>

        {/* Footer */}
        <footer className="mt-12 text-center text-slate-600 dark:text-slate-400 text-sm">
          <p>
            Built with{" "}
            <a
              href="https://docs.pycord.dev/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-indigo-600 dark:text-indigo-400 hover:underline"
            >
              Py-cord
            </a>
            {" "}and Google Speech Recognition
          </p>
        </footer>
      </div>
    </div>
  );
}
