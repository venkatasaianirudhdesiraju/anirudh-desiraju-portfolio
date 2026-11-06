import { Award, GraduationCap, MapPin } from "lucide-react";
import { profile } from "@/lib/data";
import Reveal from "@/components/Reveal";
import SectionHeading from "@/components/SectionHeading";

const facts = [
  { icon: MapPin, label: "Based in", value: profile.location },
  { icon: Award, label: "Certified", value: profile.certifications[0] },
  { icon: GraduationCap, label: "Education", value: `${profile.education.degree}, ${profile.education.school}` },
];

export default function About() {
  return (
    <section id="about" className="relative mx-auto max-w-5xl px-6 py-28">
      <SectionHeading index="01" title="About" subtitle="The short version." />

      <div className="grid gap-10 md:grid-cols-5">
        <Reveal delay={0.1} className="md:col-span-2">
          <div className="group relative aspect-square w-full max-w-xs overflow-hidden rounded-2xl border border-border bg-surface">
            <div className="absolute inset-0 flex items-center justify-center font-mono text-6xl font-bold text-border transition-colors group-hover:text-accent/30">
              {profile.initials}
            </div>
            <div className="absolute inset-0 grid-bg opacity-40" />
            <div className="absolute bottom-0 left-0 right-0 border-t border-border bg-background/70 p-3 font-mono text-xs text-muted backdrop-blur">
              {profile.yearsExperience}+ yrs · Python / AWS / Data
            </div>
          </div>
        </Reveal>

        <Reveal delay={0.2} className="md:col-span-3">
          <p className="text-lg leading-relaxed text-foreground/90">{profile.summary}</p>
          <p className="mt-4 leading-relaxed text-muted">
            Outside of client work, I self-host a fork of Odysseus, an open-source AI workspace, and
            built the six tools in{" "}
            <a href="#work" className="text-accent underline-offset-4 hover:underline">
              the Lab
            </a>{" "}
            below — including this portfolio&apos;s chat widget, which runs on a local Llama model on
            my own desktop. No cloud API, no data leaving this machine.
          </p>

          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            {facts.map(({ icon: Icon, label, value }) => (
              <div
                key={label}
                className="rounded-xl border border-border bg-surface/60 p-4 transition-colors hover:border-accent/50"
              >
                <Icon className="h-4 w-4 text-accent" />
                <div className="mt-2 font-mono text-[11px] uppercase tracking-wide text-muted">
                  {label}
                </div>
                <div className="mt-1 text-sm">{value}</div>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
