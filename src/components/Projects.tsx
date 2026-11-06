"use client";

import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";
import { flagshipProject, labProjects, profile, projects } from "@/lib/data";
import { withBasePath } from "@/lib/basePath";
import { useHub } from "@/lib/useHub";
import Reveal from "@/components/Reveal";
import SectionHeading from "@/components/SectionHeading";
import { GithubGlyph } from "@/components/icons/Brand";

export default function Projects() {
  const hub = useHub();
  return (
    <section id="work" className="relative mx-auto max-w-5xl px-6 py-28">
      <SectionHeading
        index="03"
        title="Selected work"
        subtitle="One flagship project I maintain, things built on the job, and a lab of open-source tools."
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
                // eslint-disable-next-line @next/next/no-img-element -- static export + basePath need a plain <img>
                <img
                  src={withBasePath(flagshipProject.image)}
                  alt={`${flagshipProject.name} interface screenshot`}
                  className="absolute inset-0 h-full w-full object-cover transition-transform duration-700 group-hover:scale-[1.03]"
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
      <Reveal>
        <div className="mt-20 flex flex-wrap items-end justify-between gap-4">
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
    </section>
  );
}
