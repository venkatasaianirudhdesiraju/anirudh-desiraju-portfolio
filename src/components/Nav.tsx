"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Menu, Moon, Sun, Terminal, X } from "lucide-react";
import { navLinks, profile } from "@/lib/data";
import { useTheme } from "@/components/ThemeProvider";

export default function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState<string>("");
  const [menuOpen, setMenuOpen] = useState(false);
  const { theme, toggle } = useTheme();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const sections = navLinks
      .map((l) => document.querySelector(l.href))
      .filter(Boolean) as Element[];
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActive(`#${entry.target.id}`);
          }
        });
      },
      { rootMargin: "-40% 0px -50% 0px", threshold: 0 }
    );
    sections.forEach((s) => observer.observe(s));
    return () => observer.disconnect();
  }, []);

  return (
    <motion.header
      initial={{ y: -40, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className={`fixed inset-x-0 top-0 z-50 transition-all duration-300 ${
        scrolled ? "py-3" : "py-5"
      }`}
    >
      <div
        className={`mx-auto flex max-w-5xl items-center justify-between rounded-2xl px-4 transition-all duration-300 sm:px-6 ${
          scrolled ? "glass border border-border py-2.5 shadow-lg shadow-black/10" : "py-1"
        }`}
      >
        <a href="#top" className="flex items-center gap-2 font-mono text-sm font-medium">
          <Terminal className="h-4 w-4 text-accent" />
          <span className="hidden sm:inline">{profile.shortName}</span>
          <span className="text-accent">.dev</span>
        </a>

        <nav className="hidden items-center gap-1 md:flex">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className={`relative rounded-lg px-3 py-1.5 font-mono text-xs transition-colors ${
                active === link.href
                  ? "text-foreground"
                  : "text-muted hover:text-foreground"
              }`}
            >
              {active === link.href && (
                <motion.span
                  layoutId="nav-pill"
                  className="absolute inset-0 rounded-lg bg-surface-2"
                  transition={{ type: "spring", stiffness: 350, damping: 30 }}
                />
              )}
              <span className="relative">{link.label}</span>
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <button
            onClick={toggle}
            aria-label="Toggle theme"
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-border text-muted transition-colors hover:text-accent"
          >
            {theme === "dark" ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
          </button>
          <a
            href={profile.resumeHref}
            download
            className="hidden rounded-lg border border-border px-3 py-1.5 font-mono text-xs text-muted transition-colors hover:border-accent hover:text-accent sm:inline-block"
          >
            Resume
          </a>
          <button
            onClick={() => setMenuOpen((o) => !o)}
            aria-label="Toggle menu"
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-border text-muted transition-colors hover:text-accent md:hidden"
          >
            {menuOpen ? <X className="h-3.5 w-3.5" /> : <Menu className="h-3.5 w-3.5" />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {menuOpen && (
          <motion.nav
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="mx-4 mt-2 flex flex-col overflow-hidden rounded-2xl border border-border bg-surface shadow-xl shadow-black/20 sm:mx-6 md:hidden"
          >
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={() => setMenuOpen(false)}
                className={`border-b border-border px-5 py-3 font-mono text-sm last:border-b-0 ${
                  active === link.href ? "text-accent" : "text-foreground/85"
                }`}
              >
                {link.label}
              </a>
            ))}
            <a
              href={profile.resumeHref}
              download
              onClick={() => setMenuOpen(false)}
              className="px-5 py-3 font-mono text-sm text-accent"
            >
              Download Resume
            </a>
          </motion.nav>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
