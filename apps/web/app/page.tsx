"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Bot, SearchCheck, ShieldCheck, Sparkles } from "lucide-react";

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
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
      <div className="mb-3 flex items-center gap-2 text-sm text-slate-500">
        <Sparkles className="h-4 w-4 text-accent" />
        Live Chat Preview
      </div>
      <div className="space-y-3">
        <div className="ml-auto max-w-xs rounded-2xl bg-primary px-4 py-2 text-sm text-white">Is there any scholarship for degree students?</div>
        <motion.div
          initial={{ opacity: 0.4 }}
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 1.4, repeat: Infinity }}
          className="max-w-sm rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-700"
        >
          I can confirm one official scheme notification. Version and source attached.
        </motion.div>
      </div>
    </div>
  );
}

export default function HomePage() {
  return (
    <div className="space-y-16 pb-6">
      <section className="grid gap-8 lg:grid-cols-2 lg:items-center">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
          <p className="mb-4 inline-flex rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600">
            Andhra Pradesh Student Welfare Intelligence
          </p>
          <h1 className="text-4xl font-bold leading-tight text-slateText sm:text-5xl">Find Government Schemes in Seconds</h1>
          <p className="mt-4 text-lg text-slate-600">Official. Verified. Updated.</p>
          <div className="mt-6">
            <Link href="/chat">
              <Button size="lg">Start Checking Eligibility</Button>
            </Link>
          </div>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }}>
          <HeroPreview />
        </motion.div>
      </section>

      <section>
        <h2 className="mb-6 text-2xl font-bold">How It Works</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {howItWorks.map((item, idx) => {
            const Icon = item.icon;
            return (
              <motion.div key={item.title} initial={{ opacity: 0, y: 14 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.08 }} viewport={{ once: true }}>
                <Card className="h-full transition hover:-translate-y-1">
                  <CardHeader>
                    <div className="mb-3 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                      <Icon className="h-5 w-5" />
                    </div>
                    <CardTitle>{item.title}</CardTitle>
                    <CardDescription>{item.description}</CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
        <h2 className="mb-6 text-2xl font-bold">Trust & Transparency</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {trust.map((item) => (
            <Card key={item.title} className="bg-slate-50">
              <CardHeader>
                <CardTitle>{item.title}</CardTitle>
                <CardDescription>{item.description}</CardDescription>
              </CardHeader>
              <CardContent />
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}

