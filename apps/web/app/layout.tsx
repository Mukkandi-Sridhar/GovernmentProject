import type { Metadata } from "next";
import { Public_Sans } from "next/font/google";

import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { AppQueryProvider } from "@/lib/query-provider";

import "./globals.css";

const publicSans = Public_Sans({ subsets: ["latin"], variable: "--font-public-sans" });

export const metadata: Metadata = {
  title: "Andhra Pradesh Welfare AI",
  description: "Official, verified, and traceable civic AI assistant for student welfare schemes",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={publicSans.variable}>
      <body className="min-h-screen font-sans text-slateText">
        <AppQueryProvider>
          <SiteHeader />
          <main className="mx-auto min-h-[calc(100vh-170px)] max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</main>
          <SiteFooter />
        </AppQueryProvider>
      </body>
    </html>
  );
}

