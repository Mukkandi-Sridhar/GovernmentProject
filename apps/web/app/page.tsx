"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Bot, SearchCheck, ShieldCheck, Sparkles, ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const howItWorks = [
  {
    icon: SearchCheck,
    title: "Discover",
    description: "Autonomous crawling discovers official Andhra Pradesh scheme announcements and notifications.",
  },
  {
    icon: ShieldCheck,
    title: "Verify",
    description: "AI extracts only explicit data and nullifies unsupported claims through evidence matching.",
  },
  {
    icon: Bot,
    title: "Apply",
    description: "Citational chat responses help students understand confirmed details in seconds.",
  },
];

const trust = [
  {
    title: "Official Sources Only",
    description: "Data is sourced from allowlisted government hosts with strict crawl boundaries.",
  },
  {
    title: "Version Controlled Data",
    description: "Every scheme update is immutable, diffed, and traceable to prior versions.",
  },
  {
    title: "No Hallucination AI",
    description: "The assistant refuses to invent eligibility or deadlines when evidence is absent.",
  },
  {
    title: "Source Traceable",
    description: "All answers carry source URL, version number, and last updated metadata.",
  },
];

function HeroPreview() {
  return (
    <div className="relative rounded-3xl border border-white/40 bg-white/60 p-6 shadow-glass backdrop-blur-xl">
      <div className="absolute -top-4 -right-4 h-24 w-24 rounded-full bg-accent/20 blur-2xl" />
      <div className="absolute -bottom-6 -left-6 h-32 w-32 rounded-full bg-primary/20 blur-3xl" />

      <div className="relative z-10 mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold text-primary">
          <Sparkles className="h-4 w-4 animate-pulse-slow" />
          Live Chat Session
        </div>
        <div className="h-2 w-2 rounded-full bg-accent animate-pulse" />
      </div>

      <div className="relative z-10 space-y-4">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="ml-auto w-11/12 max-w-[280px] rounded-2xl rounded-tr-sm bg-primary p-4 text-sm text-white shadow-soft"
        >
          Is there any scholarship for degree students in AP?
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 1.2, duration: 0.5 }}
          className="mr-auto w-11/12 max-w-[320px] rounded-2xl rounded-tl-sm border border-slate-200 bg-white/80 p-4 text-sm text-slate-700 shadow-soft backdrop-blur-md"
        >
          <div className="mb-2 flex gap-1">
            <div className="h-1.5 w-1.5 rounded-full bg-primary/40 animate-bounce" />
            <div className="h-1.5 w-1.5 rounded-full bg-primary/40 animate-bounce [animation-delay:-0.15s]" />
            <div className="h-1.5 w-1.5 rounded-full bg-primary/40 animate-bounce [animation-delay:-0.3s]" />
          </div>
          Yes, I found 2 official scheme notifications for degree students. Here are the confirmed details and source documents...
        </motion.div>
      </div>
    </div>
  );
}

export default function HomePage() {
  return (
    <div className="space-y-24 pb-12 pt-8">
      <section className="grid gap-12 lg:grid-cols-2 lg:items-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="relative z-10"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.4 }}
            className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/10 bg-primary/5 px-4 py-1.5 text-xs font-semibold text-primary shadow-sm backdrop-blur-md"
          >
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-primary"></span>
            </span>
            AP Student Welfare Intelligence
          </motion.div>

          <h1 className="text-5xl font-extrabold tracking-tight text-slateText sm:text-6xl lg:leading-[1.1]">
            Find Government Schemes in <span className="text-primary">Seconds</span>
          </h1>

          <p className="mt-6 text-xl text-slate-600 font-medium leading-relaxed max-w-lg">
            Official. Verified. Updated. Get instant, citational answers about Andhra Pradesh student welfare.
          </p>

          <div className="mt-8 flex flex-col sm:flex-row gap-4">
            <Link href="/chat">
              <Button size="lg" className="w-full sm:w-auto group">
                Start Checking Eligibility
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link href="/admin/schemes">
              <Button size="lg" variant="secondary" className="w-full sm:w-auto">
                Browse Schemes
              </Button>
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
          className="relative"
        >
          <HeroPreview />
        </motion.div>
      </section>

      <section>
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-slateText">How It Works</h2>
          <p className="mt-4 text-slate-500">A completely autonomous and verified pipeline.</p>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {howItWorks.map((item, idx) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1, duration: 0.5 }}
                viewport={{ once: true }}
              >
                <Card className="h-full border-slate-200/60 bg-white/50 shadow-soft backdrop-blur-xl transition-all duration-300 hover:-translate-y-2 hover:shadow-glass">
                  <CardHeader>
                    <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary transition-colors hover:bg-primary hover:text-white">
                      <Icon className="h-6 w-6" />
                    </div>
                    <CardTitle className="text-xl">{item.title}</CardTitle>
                    <CardDescription className="text-base leading-relaxed">{item.description}</CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </section>

      <section className="relative overflow-hidden rounded-3xl border border-white/40 bg-white/60 p-8 shadow-glass backdrop-blur-xl sm:p-12">
        <div className="absolute top-0 right-0 -m-20 h-40 w-40 rounded-full bg-primary/5 blur-3xl" />
        <div className="relative z-10 mb-10 md:w-2/3">
          <h2 className="text-3xl font-bold tracking-tight text-slateText">Trust & Transparency</h2>
          <p className="mt-4 text-lg text-slate-600">Built on principles that ensure 100% accurate information for students.</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 relative z-10">
          {trust.map((item, idx) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, x: -10 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1, duration: 0.4 }}
              viewport={{ once: true }}
            >
              <Card className="h-full border-slate-200/50 bg-white/40 backdrop-blur-md transition-colors hover:bg-white/80">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3 text-lg">
                    <ShieldCheck className="h-5 w-5 text-accent" />
                    {item.title}
                  </CardTitle>
                  <CardDescription className="text-sm leading-relaxed text-slate-600">
                    {item.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}

