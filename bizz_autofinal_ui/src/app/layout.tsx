import type { Metadata } from "next";
import { Inter } from "next/font/google";
// @ts-ignore - allow side-effect CSS import
import "./globals.css";
import { cn } from "@/lib/utils";
import { ToasterProvider } from "@/components/ui/toaster";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "AutoBiz - #1 Business Automation Platform in Pakistan",
  description:
    "The complete B2B automation platform for Pakistani traders and distributors.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={cn(
          "min-h-screen bg-white font-sans antialiased dark:bg-gray-950",
          inter.variable
        )}
      >
        {children}
           <ToasterProvider />
      </body>
    </html>
  );
}
