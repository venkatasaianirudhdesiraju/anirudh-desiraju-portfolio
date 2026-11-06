"use client";

import { motion } from "framer-motion";
import { ArrowUpRight, Mail, Phone } from "lucide-react";
import { profile } from "@/lib/data";
import Reveal from "@/components/Reveal";
import SectionHeading from "@/components/SectionHeading";
import { GithubGlyph, LinkedinGlyph } from "@/components/icons/Brand";

const links = [
  { label: "Email", value: profile.email, href: `mailto:${profile.email}`, icon: Mail },
  { label: "Phone", value: profile.phone, href: `tel:${profile.phone.replace(/[^\d+]/g, "")}`, icon: Phone },
  { label: "LinkedIn", value: "/in/anirudhdesiraju", href: profile.linkedin, icon: LinkedinGlyph },
  { label: "GitHub", value: "@venkatasaianirudhdesiraju", href: profile.github, icon: GithubGlyph },
];

export default function Contact() {
  return (
    <section id="contact" className="relative mx-auto max-w-5xl px-6 py-28">
      <SectionHeading
        index="05"
        title="Let's talk"
        subtitle="Open to senior backend / Python roles and interesting infrastructure problems."
      />

      <Reveal>
        <div className="relative overflow-hidden rounded-3xl border border-border bg-surface p-10 sm:p-14">
          <div className="absolute -right-24 -top-24 h-64 w-64 rounded-full bg-accent/10 blur-[100px]" />
          <h3 className="max-w-md text-3xl font-semibold tracking-tight sm:text-4xl">
            Got something worth building?{" "}
            <span className="text-gradient">Reach out.</span>
          </h3>
          <p className="mt-4 max-w-md text-muted">
            I reply fastest to email. Happy to talk through the role, the stack, or just trade
            notes on self-hosted AI tooling.
          </p>

          <div className="mt-8 grid gap-3 sm:grid-cols-2">
            {links.map(({ label, value, href, icon: Icon }, i) => (
              <motion.a
                key={label}
                href={href}
                target={href.startsWith("http") ? "_blank" : undefined}
                rel="noreferrer"
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.06, duration: 0.5 }}
                className="group flex items-center justify-between rounded-xl border border-border bg-background/40 px-4 py-3.5 transition-colors hover:border-accent/50"
              >
                <span className="flex items-center gap-3">
                  <Icon className="h-4 w-4 text-accent" />
                  <span>
                    <div className="text-[11px] uppercase tracking-wide text-muted">{label}</div>
                    <div className="font-mono text-sm">{value}</div>
                  </span>
                </span>
                <ArrowUpRight className="h-4 w-4 text-muted transition-all group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-accent" />
              </motion.a>
            ))}
          </div>
        </div>
      </Reveal>
    </section>
  );
}
