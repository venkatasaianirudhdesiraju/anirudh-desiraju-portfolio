"""In-process token bucket per key. For multiple workers, back this with Redis (same interface)."""
from __future__ import annotations

import threading
import time


class TokenBucket:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.state: dict[str, tuple[float, float]] = {}  # key -> (tokens, last_ts)
        self.lock = threading.Lock()

    def allow(self, key: str, per_minute: int) -> tuple[bool, float]:
        """Returns (allowed, seconds_until_next_token)."""
        rate = per_minute / 60.0
        with self.lock:
            tokens, last = self.state.get(key, (float(per_minute), self.clock()))
            t = self.clock()
            tokens = min(per_minute, tokens + (t - last) * rate)
            if tokens >= 1:
                self.state[key] = (tokens - 1, t)
                return True, 0.0
            self.state[key] = (tokens, t)
            return False, (1 - tokens) / rate
