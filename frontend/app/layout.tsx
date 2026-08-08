import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "CTF-OS", description: "AI-native CTF investigation console" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
