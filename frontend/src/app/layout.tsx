import type { Metadata } from "next";
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

export const metadata: Metadata = {
  title: "OpenIntel | OSINT Platform",
  description: "Enterprise Open Source Intelligence Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col`}
      >
        <header className="w-full border-b border-panel-border bg-panel py-4 px-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Minimalist Logo */}
            <div className="w-8 h-8 rounded border-2 border-accent flex items-center justify-center">
              <span className="text-accent font-mono font-bold text-lg leading-none">O</span>
            </div>
            <h1 className="text-xl font-mono font-semibold tracking-widest text-foreground">
              OPEN<span className="text-accent glow-text">INTEL</span>
            </h1>
          </div>
          <nav className="flex gap-6 text-sm font-mono text-gray-400">
            <a href="/" className="hover:text-accent transition-colors">SEARCH</a>
            <a href="/reports" className="hover:text-accent transition-colors">REPORTS</a>
            <a href="/graph" className="hover:text-accent transition-colors">GRAPH</a>
            <a href="#" className="hover:text-accent transition-colors opacity-50 cursor-not-allowed">SETTINGS</a>
          </nav>
        </header>

        <main className="flex-1 flex flex-col items-center justify-center p-8">
          {children}
        </main>
        
        <footer className="w-full border-t border-panel-border bg-panel py-4 text-center text-xs text-gray-600 font-mono">
          © {new Date().getFullYear()} OpenIntel. Restricted Access.
        </footer>
      </body>
    </html>
  );
}
