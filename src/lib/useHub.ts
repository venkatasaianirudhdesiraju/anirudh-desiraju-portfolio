"use client";

import { useEffect, useState } from "react";

/** The Hub only exists on the owner's machine; on any public host this stays offline and nothing is shown. */
export function useHub() {
  const [hub, setHub] = useState<{ online: boolean; url?: string }>({ online: false });
  useEffect(() => {
    fetch("/api/hub-status")
      .then((r) => r.json())
      .then(setHub)
      .catch(() => setHub({ online: false }));
  }, []);
  return hub;
}
