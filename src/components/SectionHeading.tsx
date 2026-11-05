import Reveal from "@/components/Reveal";

export default function SectionHeading({
  index,
  title,
  subtitle,
}: {
  index: string;
  title: string;
  subtitle?: string;
}) {
  return (
    <Reveal className="mb-12">
      <div className="flex items-baseline gap-3 font-mono text-sm text-accent">
        <span>{index}</span>
        <span className="h-px flex-1 max-w-10 bg-border" />
      </div>
      <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">{title}</h2>
      {subtitle && <p className="mt-3 max-w-xl text-muted">{subtitle}</p>}
    </Reveal>
  );
}
