"use client";

import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";
import { labProjects, profile, projects } from "@/lib/data";
import { useHub } from "@/lib/useHub";
import Reveal from "@/components/Reveal";
import SectionHeading from "@/components/SectionHeading";

export default function Projects() {
  const hub = useHub();
  return (
    <section id="work" className="relative mx-auto max-w-5xl px-6 py-28">
      <SectionHeading
        index="03"
        title="Selected work"
        subtitle="A lab of open-source tools I built and run locally, plus things built on the job."
      />

      <Reveal>
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h3 className="text-xl font-semibold tracking-tight">The Lab</h3>
            <p className="mt-1 max-w-xl text-sm text-muted">
              Six open-source tools I built and run together behind one local launcher, covering ML,
              NLP, data quality, APIs and product engineering. Each has tests, a CLI or REST API, and docs.
            </p>
          </div>
          {hub.online && (
            <a href={hub.url} target="_blank" rel="noreferrer"
               className="rounded-lg border border-accent/40 bg-accent/10 px-3 py-1.5 font-mono text-xs text-accent hover:bg-accent/20">
              Open the Hub ↗
            </a>
          )}
        </div>
      </Reveal>

      <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {labProjects.map((p, i) => {
          const href = hub.online ? `${hub.url}${p.hubPath}` : p.href ?? `${profile.github}`;
          return (
            <Reveal key={p.name} delay={0.05 + i * 0.06}>
              <motion.a
                href={href}
                target="_blank"
                rel="noreferrer"
                whileHover={{ y: -6 }}
                transition={{ type: "spring", stiffness: 300, damping: 22 }}
                className="group flex h-full flex-col rounded-2xl border border-border bg-surface/60 p-6 transition-colors hover:border-accent/40"
              >
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">{p.name}</h4>
                  <ArrowUpRight className="h-4 w-4 text-muted transition-all group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-accent" />
                </div>
                <p className="mt-1 text-xs font-mono text-accent/80">{p.tagline}</p>
                <p className="mt-3 flex-1 text-sm leading-relaxed text-muted">{p.description}</p>
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {p.stack.map((s) => (
                    <span key={s} className="chip rounded-md border border-border px-2 py-1 text-muted">{s}</span>
                  ))}
                </div>
              </motion.a>
            </Reveal>
          );
        })}
      </div>

      <Reveal>
        <h3 className="mt-20 text-xl font-semibold tracking-tight">On the job</h3>
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
