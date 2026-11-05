import { skills } from "@/lib/data";
import Reveal from "@/components/Reveal";
import SectionHeading from "@/components/SectionHeading";

const marqueeItems = skills.flatMap((g) => g.skills);

export default function Skills() {
  return (
    <section id="skills" className="relative py-28">
      <div className="mx-auto max-w-5xl px-6">
        <SectionHeading
          index="04"
          title="Toolbox"
          subtitle="What I reach for day to day, grouped by where it lives in the stack."
        />

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {skills.map((group, i) => (
            <Reveal key={group.category} delay={i * 0.06}>
              <div className="h-full rounded-2xl border border-border bg-surface/60 p-5 transition-colors hover:border-accent/40">
                <h4 className="font-mono text-xs uppercase tracking-wide text-accent">
                  {group.category}
                </h4>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {group.skills.map((s) => (
                    <span
                      key={s}
                      className="rounded-md border border-border bg-background/40 px-2 py-1 text-xs text-foreground/85"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>

      <div className="relative mt-14 overflow-hidden border-y border-border py-5">
        <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-24 bg-gradient-to-r from-background to-transparent" />
        <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-24 bg-gradient-to-l from-background to-transparent" />
        <div className="flex w-max animate-marquee gap-10 font-mono text-sm text-muted">
          {[...marqueeItems, ...marqueeItems].map((s, i) => (
            <span key={`${s}-${i}`} className="flex items-center gap-10 whitespace-nowrap">
              {s}
              <span className="text-accent">/</span>
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
