import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Groww AI Companion | Mutual Fund Assistant",
  description: "Factual information about GROW Mutual Funds with strict non-advisory compliance.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className={`${inter.className} min-h-full flex flex-col bg-groww-black`}>
        {children}
      </body>
    </html>
  );
}
