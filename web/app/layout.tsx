import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Dufu - Discord Voice Transcription Bot",
  description: "Record and transcribe voice conversations in your Discord server. Join voice channels, capture audio, and get real-time speech-to-text transcriptions.",
  keywords: [
    "Discord bot",
    "voice transcription",
    "speech to text",
    "voice recording",
    "Discord voice",
    "audio transcription",
    "voice channel recorder",
    "Discord automation",
  ],
  authors: [{ name: "Dufu Bot" }],
  creator: "Dufu",
  publisher: "Dufu",
  metadataBase: new URL("https://dufu.vercel.app"), // TODO: Replace with your actual domain
  openGraph: {
    title: "Dufu - Discord Voice Transcription Bot",
    description: "Record and transcribe voice conversations in your Discord server. Join voice channels, capture audio, and get real-time speech-to-text transcriptions.",
    url: "https://dufu.vercel.app", // TODO: Replace with your actual domain
    siteName: "Dufu",
    images: [
      {
        url: "/og-image.png", // TODO: Create an Open Graph image (1200x630px)
        width: 1200,
        height: 630,
        alt: "Dufu Discord Bot - Voice Transcription",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Dufu - Discord Voice Transcription Bot",
    description: "Record and transcribe voice conversations in your Discord server.",
    images: ["/og-image.png"], // TODO: Create a Twitter card image
  },
  icons: {
    icon: [
      { url: "/icon.png", sizes: "any" },
      { url: "/icon-16x16.png", sizes: "16x16", type: "image/png" }, // TODO: Create these icon files
      { url: "/icon-32x32.png", sizes: "32x32", type: "image/png" },
    ],
    apple: [
      { url: "/apple-icon.png", sizes: "180x180", type: "image/png" }, // TODO: Create Apple touch icon
    ],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  verification: {
    // TODO: Add verification codes if you have them
    // google: "your-google-verification-code",
    // yandex: "your-yandex-verification-code",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Navbar />  
        {children}
      </body>
    </html>
  );
}
