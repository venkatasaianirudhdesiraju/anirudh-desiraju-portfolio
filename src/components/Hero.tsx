"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ArrowDown, Download, Mail } from "lucide-react";
import { profile } from "@/lib/data";
import { GithubGlyph, LinkedinGlyph } from "@/components/icons/Brand";

const ROLES = [
  "Senior Python Developer",
  "Backend & API Architect",
  "Data / ML Pipeline Engineer",
  "AWS Certified Developer",
  "Open-Source Maintainer",
];

function useTypewriter(words: string[]) {
  const [index, setIndex] = useState(0);
  const [text, setText] = useState("");
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const current = words[index % words.length];
    const speed = deleting ? 35 : 65;
    const pause = 1400;

    if (!deleting && text === current) {
      const t = setTimeout(() => setDeleting(true), pause);
      return () => clearTimeout(t);
    }
    if (deleting && text === "") {
      setDeleting(false);
      setIndex((i) => i + 1);
      return;
    }
    const t = setTimeout(() => {
      setText((prev) =>
        deleting ? current.slice(0, prev.length - 1) : current.slice(0, prev.length + 1)
      );
    }, speed);
    return () => clearTimeout(t);
  }, [text, deleting, index, words]);

  return text;
}

export default function Hero() {
  const typed = useTypewriter(ROLES);

  return (
    <section id="top" className="relative flex min-h-screen flex-col justify-center px-6 pt-24">
      <div className="mx-auto w-full max-w-5xl">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-6 inline-flex items-center gap-2 self-start rounded-full border border-border bg-surface/60 px-3 py-1 font-mono text-xs text-muted"
        >
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
          </span>
          open to select opportunities · {profile.location}
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="text-5xl font-semibold leading-[1.05] tracking-tight sm:text-7xl"
        >
          Hi, I&apos;m <span className="text-gradient">{profile.name.split(" ")[0]}</span>.
          <br />
          I build systems that <span className="text-gradient">ship, scale &amp; hold up</span>.
        </motion.h1>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-6 flex h-7 items-center font-mono text-base text-muted sm:text-lg"
        >
          <span className="mr-2 text-accent">$</span>
          <span>{typed}</span>
          <span className="ml-0.5 h-5 w-[2px] animate-blink bg-accent" />
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-6 max-w-2xl text-balance text-base text-muted sm:text-lg"
        >
          {profile.summary}
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mt-10 flex flex-wrap items-center gap-3"
        >
          <a
            href="#work"
            className="group inline-flex items-center gap-2 rounded-xl bg-accent px-5 py-3 font-mono text-sm font-medium text-[#0a0a0a] transition-transform hover:-translate-y-0.5 hover:shadow-lg hover:shadow-accent/20"
          >
            View my work
            <ArrowDown className="h-3.5 w-3.5 transition-transform group-hover:translate-y-0.5" />
          </a>
          <a
            href={profile.resumeHref}
            download
            className="inline-flex items-center gap-2 rounded-xl border border-border px-5 py-3 font-mono text-sm text-foreground transition-colors hover:border-accent hover:text-accent"
          >
            <Download className="h-3.5 w-3.5" />
            Resume
          </a>
          <div className="ml-1 flex items-center gap-1">
            {[
              { href: profile.github, icon: GithubGlyph, label: "GitHub" },
              { href: profile.linkedin, icon: LinkedinGlyph, label: "LinkedIn" },
              { href: `mailto:${profile.email}`, icon: Mail, label: "Email" },
            ].map(({ href, icon: Icon, label }) => (
              <a
                key={label}
                href={href}
                target={href.startsWith("http") ? "_blank" : undefined}
                rel="noreferrer"
                aria-label={label}
                className="flex h-11 w-11 items-center justify-center rounded-xl border border-transparent text-muted transition-colors hover:border-border hover:text-accent"
              >
                <Icon className="h-4 w-4" />
              </a>
            ))}
          </div>
        </motion.div>
      </div>

      <motion.a
        href="#about"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 0.8 }}
        className="absolute bottom-10 left-1/2 -translate-x-1/2 text-muted"
        aria-label="Scroll down"
      >
        <motion.div animate={{ y: [0, 8, 0] }} transition={{ repeat: Infinity, duration: 2 }}>
          <ArrowDown className="h-5 w-5" />
        </motion.div>
      </motion.a>
    </section>
  );
}
