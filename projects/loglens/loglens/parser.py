"""Extract individual failures from raw test logs and normalize them into signatures."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# Lines that mark the start of a failure block in common runners (pytest, unittest, JUnit, generic).
FAILURE_START = re.compile(
    r"^(?:_{3,}\s*(?P<pytest>\S+)\s*_{3,}"          # pytest: ____ test_name ____
    r"|(?:FAIL|ERROR):\s*(?P<unittest>\S+)"          # unittest: FAIL: test_x (mod.Class)
    r"|\[(?:FAIL|FAILED|ERROR)\]\s*(?P<generic>\S+)"  # generic: [FAIL] test_name
    r"|Tests run:.*FAILURE!.*in\s+(?P<junit>\S+))",   # JUnit/Maven summary line
    re.IGNORECASE,
)
SECTION_END = re.compile(r"^={5,}")  # pytest "==== short test summary ====" etc.
LOCATION_LINE = re.compile(r"^\S+:\d+:\s*\w+$")  # tests/test_x.py:22: ConnectionError
SUMMARY_LINE = re.compile(r"^(?:FAILED|ERROR)\s+\S+::")
ERROR_LINE = re.compile(
    r"(?:\b\w*(?:Error|Exception|Timeout|Failure)\b|AssertionError|assert\s|FAILED|Traceback)",
)

# Normalization rules: volatile tokens → placeholders, so the same bug yields the same signature.
_NORMALIZERS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b"), "<TS>"),
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I), "<UUID>"),
    (re.compile(r"\b0x[0-9a-f]+\b", re.I), "<HEX>"),
    (re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?\b"), "<IP>"),
    (re.compile(r"(?:[A-Za-z]:)?(?:[\\/][\w.\-]+){2,}"), "<PATH>"),
    (re.compile(r"\bline \d+\b"), "line <N>"),
    (re.compile(r"\b\d+(?:\.\d+)?\b"), "<N>"),
    (re.compile(r"'[^'\n]{25,}'|\"[^\"\n]{25,}\""), "<STR>"),
]


def normalize(text: str) -> str:
    for pattern, repl in _NORMALIZERS:
        text = pattern.sub(repl, text)
    return re.sub(r"[ \t]+", " ", text).strip()


@dataclass
class Failure:
    test: str
    source: str
    body: str
    error_lines: list[str] = field(default_factory=list)

    @property
    def signature(self) -> str:
        """Normalized error lines; falls back to the last lines of the block."""
        lines = self.error_lines or self.body.strip().splitlines()[-3:]
        return normalize("\n".join(lines[:3]))

    @property
    def headline(self) -> str:
        lines = self.error_lines or self.body.strip().splitlines()[-1:] or [""]
        return lines[-1].strip()[:200]


def _error_lines(block: list[str]) -> list[str]:
    """Most specific error lines: pytest 'E ' lines first, minus location and summary noise."""
    e_lines = [ln[1:].strip() for ln in block if ln.startswith("E ")]
    if e_lines:
        return e_lines
    return [
        ln.strip() for ln in block[1:]
        if ERROR_LINE.search(ln) and not LOCATION_LINE.match(ln.strip()) and not SUMMARY_LINE.match(ln.strip())
    ]


def extract_failures(text: str, source: str = "<input>") -> list[Failure]:
    """Split a log into failure blocks. Each block runs until the next failure start."""
    failures: list[Failure] = []
    current: Failure | None = None
    buf: list[str] = []

    def flush() -> None:
        if current is not None:
            current.body = "\n".join(buf)
            current.error_lines = _error_lines(buf)
            failures.append(current)

    for line in text.splitlines():
        m = FAILURE_START.search(line)
        if SECTION_END.match(line) and current is not None:
            flush()
            current, buf = None, []
        elif m:
            flush()
            name = next(g for g in m.groups() if g)
            current, buf = Failure(test=name, source=source, body=""), [line]
        elif current is not None:
            buf.append(line)
    flush()

    # No recognizable test markers: treat each Traceback / error line as its own failure.
    if not failures:
        for i, line in enumerate(text.splitlines()):
            if ERROR_LINE.search(line):
                failures.append(Failure(test=f"line {i + 1}", source=source, body=line, error_lines=[line.strip()]))
    return failures
