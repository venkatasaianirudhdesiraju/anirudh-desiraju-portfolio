"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";
import { flagshipProject, projects } from "@/lib/data";
import Reveal from "@/components/Reveal";
import SectionHeading from "@/components/SectionHeading";
import { GithubGlyph } from "@/components/icons/Brand";

export default function Projects() {
  return (
    <section id="work" className="relative mx-auto max-w-5xl px-6 py-28">
      <SectionHeading
        index="03"
        title="Selected work"
        subtitle="One flagship project I maintain, plus a few things built on the job."
      />

      <Reveal>
        <a
          href={flagshipProject.href}
          target="_blank"
          rel="noreferrer"
          className="group relative block overflow-hidden rounded-3xl border border-border bg-surface transition-colors hover:border-accent/50"
        >
          <div className="grid gap-0 md:grid-cols-5">
            <div className="relative order-2 md:order-1 md:col-span-3 aspect-[16/11] overflow-hidden md:aspect-auto">
              {flagshipProject.image && (
                <Image
                  src={flagshipProject.image}
                  alt={`${flagshipProject.name} interface screenshot`}
                  fill
                  className="object-cover transition-transform duration-700 group-hover:scale-[1.03]"
                  sizes="(max-width: 768px) 100vw, 60vw"
                />
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-background/60 via-transparent to-transparent md:bg-gradient-to-r" />
            </div>

            <div className="order-1 flex flex-col justify-between p-7 md:order-2 md:col-span-2 md:p-8">
              <div>
                <div className="flex items-center justify-between">
                  <span className="chip rounded-full border border-accent/30 bg-accent/10 px-2.5 py-1 text-accent">
                    flagship · open source
                  </span>
                  <ArrowUpRight className="h-4 w-4 text-muted transition-all group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-accent" />
                </div>
                <h3 className="mt-4 text-2xl font-semibold tracking-tight">
                  {flagshipProject.name}
                </h3>
                <p className="mt-1 text-sm text-accent/90">{flagshipProject.tagline}</p>
                <p className="mt-4 text-sm leading-relaxed text-muted">
                  {flagshipProject.description}
                </p>
              </div>

              <div>
                {flagshipProject.stats && (
                  <div className="mt-6 grid grid-cols-3 gap-2 border-y border-border py-4">
                    {flagshipProject.stats.map((s) => (
                      <div key={s.label}>
                        <div className="font-mono text-lg font-semibold text-foreground">
                          {s.value}
                        </div>
                        <div className="text-[11px] text-muted">{s.label}</div>
                      </div>
                    ))}
                  </div>
                )}
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {flagshipProject.stack.map((s) => (
                    <span
                      key={s}
                      className="chip rounded-md border border-border px-2 py-1 text-muted"
                    >
                      {s}
                    </span>
                  ))}
                </div>
                <div className="mt-5 inline-flex items-center gap-1.5 font-mono text-xs text-muted">
                  <GithubGlyph className="h-3.5 w-3.5" /> github.com/pewdiepie-archdaemon/odysseus
                </div>
              </div>
            </div>
          </div>
        </a>
      </Reveal>

      <div className="mt-6 grid gap-5 sm:grid-cols-3">
        {projects.map((p, i) => (
          <Reveal key={p.name} delay={0.1 + i * 0.1}>
            <motion.div
              whileHover={{ y: -6 }}
              transition={{ type: "spring", stiffness: 300, damping: 22 }}
              className="h-full rounded-2xl border border-border bg-surface/60 p-6 transition-colors hover:border-accent/40"
            >
              <h4 className="font-medium">{p.name}</h4>
              <p className="mt-1 text-xs font-mono text-accent/80">{p.tagline}</p>
              <p className="mt-3 text-sm leading-relaxed text-muted">{p.description}</p>
              <div className="mt-4 flex flex-wrap gap-1.5">
                {p.stack.map((s) => (
                  <span
                    key={s}
                    className="chip rounded-md border border-border px-2 py-1 text-muted"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </motion.div>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
