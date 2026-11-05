# Anirudh Desiraju — Portfolio

A personal portfolio built with Next.js 14, TypeScript, Tailwind CSS, and Framer Motion. Content (experience, projects, skills) lives in [`src/lib/data.ts`](src/lib/data.ts) — edit that one file to update the whole site.

## Features

- Scroll-aware nav with active-section highlighting, light/dark theme toggle, mobile menu
- Animated hero with a typewriter effect and a canvas particle background
- Accordion experience timeline, flagship project showcase ([Odysseus](https://github.com/pewdiepie-archdaemon/odysseus)), project grid, skills marquee
- **Local AI chat widget** — "Ask about Anirudh" runs entirely on your own machine via [Ollama](https://ollama.com), grounded in the resume data in `src/lib/data.ts`. No cloud API, no data leaves the device.

## Running it

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Local AI chat

The chat widget talks to a local Ollama server at `http://127.0.0.1:11434` using the `llama3.1:8b` model (already pulled on this machine). To use it:

```bash
ollama serve
```

(or just have the Ollama desktop app running). If Ollama isn't reachable, the widget shows an offline state with instructions instead of failing silently — the rest of the site works normally either way.

To change the model, edit `OLLAMA_MODEL` in [`src/lib/chatContext.ts`](src/lib/chatContext.ts).

## Updating content

- **Bio, experience, projects, skills, contact info:** [`src/lib/data.ts`](src/lib/data.ts)
- **Resume PDF:** replace [`public/resume.pdf`](public/resume.pdf)
- **Chat assistant's knowledge:** auto-derived from `data.ts` via [`src/lib/chatContext.ts`](src/lib/chatContext.ts) — no separate edit needed

## Deploying

`npm run build` produces a static-friendly build. The AI chat feature only works when the site is run on this machine with Ollama serving locally — on any other host (e.g. Vercel), the widget will gracefully show as offline, and the rest of the site is unaffected.
