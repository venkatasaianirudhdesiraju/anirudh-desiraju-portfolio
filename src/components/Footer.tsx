import { profile } from "@/lib/data";

export default function Footer() {
  return (
    <footer className="border-t border-border px-6 py-8">
      <div className="mx-auto flex max-w-5xl flex-col items-center justify-between gap-2 font-mono text-xs text-muted sm:flex-row">
        <span>© {new Date().getFullYear()} {profile.name}. Built with Next.js &amp; Framer Motion.</span>
        <span>Chat widget runs locally via Ollama — nothing leaves this machine.</span>
      </div>
    </footer>
  );
}
