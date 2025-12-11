import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "WhatToWatch | Smarter movie picks",
  description:
    "Dial in the vibe, favorites, and reviews on the WhatToWatch dashboard to land the right film fast.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} bg-[#0a0e1a] text-[#e8eaf6] antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
