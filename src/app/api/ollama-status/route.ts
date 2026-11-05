import { NextResponse } from "next/server";
import { OLLAMA_HOST, OLLAMA_MODEL } from "@/lib/chatContext";

export async function GET() {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 2500);
    const res = await fetch(`${OLLAMA_HOST}/api/tags`, { signal: controller.signal });
    clearTimeout(timeout);

    if (!res.ok) {
      return NextResponse.json({ online: false, hasModel: false });
    }

    const data = (await res.json()) as { models?: { name: string }[] };
    const hasModel = (data.models ?? []).some((m) => m.name.startsWith(OLLAMA_MODEL.split(":")[0]));

    return NextResponse.json({ online: true, hasModel, model: OLLAMA_MODEL });
  } catch {
    return NextResponse.json({ online: false, hasModel: false });
  }
}
