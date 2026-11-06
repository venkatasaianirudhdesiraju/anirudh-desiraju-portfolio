import { NextResponse } from "next/server";

const HUB_URL = process.env.HUB_URL ?? "http://127.0.0.1:8000";

export async function GET() {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 1500);
    const res = await fetch(`${HUB_URL}/health`, { signal: controller.signal, cache: "no-store" });
    clearTimeout(timeout);
    const data = res.ok ? ((await res.json()) as { app?: string }) : null;
    return NextResponse.json({ online: data?.app === "hub", url: HUB_URL.replace("127.0.0.1", "localhost") });
  } catch {
    return NextResponse.json({ online: false });
  }
}
