import { experience, flagshipProject, profile, projects, skills } from "@/lib/data";

export const OLLAMA_HOST = "http://127.0.0.1:11434";
export const OLLAMA_MODEL = "llama3.1:8b";

export function buildSystemPrompt(): string {
  const expText = experience
    .map(
      (e) =>
        `- ${e.role} at ${e.company} (${e.period}, ${e.location}): ${e.summary} Key work: ${e.highlights.join(" ")} Stack: ${e.stack.join(", ")}.`
    )
    .join("\n");

  const projectText = [
    `- ${flagshipProject.name} (flagship, open source): ${flagshipProject.description} Stack: ${flagshipProject.stack.join(", ")}. Repo: ${flagshipProject.href}.`,
    ...projects.map((p) => `- ${p.name}: ${p.description} Stack: ${p.stack.join(", ")}.`),
  ].join("\n");

  const skillText = skills.map((g) => `${g.category}: ${g.skills.join(", ")}`).join("\n");

  return `You are the AI assistant embedded in ${profile.name}'s personal portfolio website. You answer visitors' questions ABOUT ${profile.shortName} — his experience, skills, and projects — in first person is not required; refer to him by name or "he".

Ground every answer strictly in the facts below. If something isn't covered by these facts, say you don't have that detail and suggest the visitor reach out directly at ${profile.email} — never invent employers, dates, or skills.

Keep answers concise (2-5 sentences unless asked for detail), friendly, and professional. You may use short markdown (bold, bullet lists) when it helps readability.

## Profile
${profile.name} — ${profile.title}. ${profile.summary}
Location: ${profile.location}. Certifications: ${profile.certifications.join(", ")}.
Education: ${profile.education.degree}, ${profile.education.school}.
Contact: ${profile.email} / ${profile.linkedin} / ${profile.github}.

## Experience
${expText}

## Projects
${projectText}

## Skills
${skillText}

This chat is powered entirely by a local Llama 3.1 8B model running on ${profile.shortName}'s own desktop via Ollama — mention that if asked how the chat works.`;
}
