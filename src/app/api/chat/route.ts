import { NextRequest } from "next/server";
import { buildSystemPrompt, OLLAMA_HOST, OLLAMA_MODEL } from "@/lib/chatContext";

export const runtime = "nodejs";

type IncomingMessage = { role: "user" | "assistant"; content: string };

export async function POST(req: NextRequest) {
  let body: { messages?: IncomingMessage[] };
  try {
    body = await req.json();
  } catch {
    return new Response("Invalid JSON body", { status: 400 });
  }

  const messages = Array.isArray(body.messages) ? body.messages : [];
  if (messages.length === 0) {
    return new Response("messages is required", { status: 400 });
  }

  const trimmed = messages
    .slice(-12)
    .filter((m) => (m.role === "user" || m.role === "assistant") && typeof m.content === "string")
    .map((m) => ({ role: m.role, content: m.content.slice(0, 4000) }));

  const ollamaPayload = {
    model: OLLAMA_MODEL,
    stream: true,
    messages: [{ role: "system", content: buildSystemPrompt() }, ...trimmed],
  };

  let upstream: Response;
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 60_000);
    upstream = await fetch(`${OLLAMA_HOST}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(ollamaPayload),
      signal: controller.signal,
    });
    req.signal.addEventListener("abort", () => controller.abort());
    clearTimeout(timeout);
  } catch {
    return new Response(
      "Ollama isn't reachable on this machine. Run `ollama serve` (or start the Ollama app) and make sure the llama3.1:8b model is pulled.",
      { status: 503 }
    );
  }

  if (!upstream.ok || !upstream.body) {
    return new Response("Ollama returned an error.", { status: 502 });
  }

  const encoder = new TextEncoder();
  const decoder = new TextDecoder();
  let buffer = "";

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const reader = upstream.body!.getReader();
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            if (!line.trim()) continue;
            try {
              const json = JSON.parse(line);
              const chunk = json?.message?.content;
              if (typeof chunk === "string" && chunk.length > 0) {
                controller.enqueue(encoder.encode(chunk));
              }
            } catch {
              // ignore malformed line
            }
          }
        }
      } catch {
        // upstream closed/aborted
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}
