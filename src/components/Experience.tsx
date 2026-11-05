"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, MapPin } from "lucide-react";
import { experience } from "@/lib/data";
import Reveal from "@/components/Reveal";
import SectionHeading from "@/components/SectionHeading";

export default function Experience() {
  const [open, setOpen] = useState<number>(0);

  return (
    <section id="experience" className="relative mx-auto max-w-5xl px-6 py-28">
      <SectionHeading
        index="02"
        title="Experience"
        subtitle="Six years across medical devices, semiconductors, and fast-moving startups."
      />

      <div className="relative">
        <div className="absolute left-[11px] top-2 bottom-2 w-px bg-border sm:left-[15px]" />

        <ul className="space-y-4">
          {experience.map((job, i) => {
            const isOpen = open === i;
            return (
              <Reveal key={job.company} delay={i * 0.08}>
                <li className="relative pl-8 sm:pl-10">
                  <span
                    className={`absolute left-0 top-5 flex h-[22px] w-[22px] sm:h-[32px] sm:w-[32px] items-center justify-center rounded-full border ${
                      job.current
                        ? "border-accent bg-accent/15"
                        : "border-border bg-surface"
                    }`}
                  >
                    <span
                      className={`h-2 w-2 rounded-full ${job.current ? "bg-accent" : "bg-muted"}`}
                    />
                  </span>

                  <button
                    onClick={() => setOpen(isOpen ? -1 : i)}
                    className={`w-full rounded-2xl border px-5 py-4 text-left transition-colors ${
                      isOpen
                        ? "border-accent/40 bg-surface"
                        : "border-border bg-surface/50 hover:border-accent/30"
                    }`}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium">{job.role}</h3>
                          {job.current && (
                            <span className="rounded-full bg-accent/15 px-2 py-0.5 font-mono text-[10px] text-accent">
                              current
                            </span>
                          )}
                        </div>
                        <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted">
                          <span className="text-foreground/80">{job.company}</span>
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" /> {job.location}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="font-mono text-xs text-muted">{job.period}</span>
                        <ChevronDown
                          className={`h-4 w-4 text-muted transition-transform ${
                            isOpen ? "rotate-180 text-accent" : ""
                          }`}
                        />
                      </div>
                    </div>

                    <AnimatePresence initial={false}>
                      {isOpen && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
                          className="overflow-hidden"
                        >
                          <p className="mt-4 text-sm text-muted">{job.summary}</p>
                          <ul className="mt-3 space-y-2">
                            {job.highlights.map((h) => (
                              <li key={h} className="flex gap-2 text-sm text-foreground/85">
                                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-accent" />
                                {h}
                              </li>
                            ))}
                          </ul>
                          <div className="mt-4 flex flex-wrap gap-1.5">
                            {job.stack.map((s) => (
                              <span
                                key={s}
                                className="chip rounded-md border border-border px-2 py-1 text-muted"
                              >
                                {s}
                              </span>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </button>
                </li>
              </Reveal>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
