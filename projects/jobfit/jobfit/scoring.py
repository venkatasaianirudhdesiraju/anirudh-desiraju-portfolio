"""Fit scoring: weighted skill coverage + semantic similarity + experience check."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .skills import find_skills

REQUIRED_HDR = re.compile(r"(?im)^\s*(?:#+\s*)?(requirements|required|must have|minimum qualifications|what you.ll need|qualifications)\b.*$")
PREFERRED_HDR = re.compile(r"(?im)^\s*(?:#+\s*)?(preferred|nice to have|bonus|plus|desired)\b.*$")
YEARS = re.compile(r"(\d{1,2})\s*\+?\s*(?:-\s*\d{1,2}\s*)?(?:years|yrs)", re.I)
STOP = {"nice", "preferred", "requirements", "required", "qualifications", "bonus", "plus", "experience", "years", "work", "team", "ability", "strong", "skills", "including", "using", "role", "job"}


@dataclass
class FitReport:
    score: float
    skill_coverage: float
    semantic_similarity: float
    required_years: int | None
    resume_years: int | None
    matched: list[str]
    missing_required: list[str]
    missing_preferred: list[str]
    keyword_gaps: list[str]
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _split_sections(jd: str) -> tuple[str, str]:
    """Return (required_text, preferred_text). If no headers, everything is 'required'."""
    req_m, pref_m = REQUIRED_HDR.search(jd), PREFERRED_HDR.search(jd)
    if pref_m and (not req_m or pref_m.start() > req_m.start()):
        return jd[: pref_m.start()], jd[pref_m.start():]
    return jd, ""


def _years(text: str, pick=max) -> int | None:
    vals = [int(v) for v in YEARS.findall(text) if 0 < int(v) < 40]
    return pick(vals) if vals else None


def _keyword_gaps(resume: str, jd: str, n: int = 12) -> list[str]:
    """Top JD terms (uni/bi-grams by TF-IDF weight) that never appear in the resume."""
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=4000, token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z+#.]{2,}\b")
    m = vec.fit_transform([jd, resume])
    terms = vec.get_feature_names_out()
    jd_w, rs = m[0].toarray()[0], resume.lower()
    ranked = sorted(((w, t) for t, w in zip(terms, jd_w) if w > 0), reverse=True)
    out = []
    for _, t in ranked:
        if t not in rs and not set(t.split()) & STOP and all(t not in o and o not in t for o in out):
            out.append(t)
        if len(out) >= n:
            break
    return out


def score(resume: str, jd: str) -> FitReport:
    req_text, pref_text = _split_sections(jd)
    jd_req, jd_pref = find_skills(req_text), find_skills(pref_text)
    jd_pref = {k: v for k, v in jd_pref.items() if k not in jd_req}
    have = find_skills(resume)

    # Required skills weigh 2x preferred; repeated mentions in the JD add a little weight.
    weights = {k: 2.0 + 0.25 * min(v - 1, 4) for k, v in jd_req.items()}
    weights.update({k: 1.0 for k in jd_pref})
    total = sum(weights.values()) or 1.0
    coverage = sum(w for k, w in weights.items() if k in have) / total

    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    sim = float(cosine_similarity(vec.fit_transform([resume, jd]))[0, 1])
    sim_scaled = min(sim / 0.45, 1.0)  # ~0.45 cosine is already a very close match for real documents

    req_years, res_years = _years(req_text, min), _years(resume, max)
    years_ok = 1.0 if req_years is None or (res_years or 0) >= req_years else max(0.0, (res_years or 0) / req_years)

    final = 100 * (0.6 * coverage + 0.25 * sim_scaled + 0.15 * years_ok)
    missing_req = sorted(jd_req.keys() - have.keys(), key=lambda k: -weights[k])
    missing_pref = sorted(jd_pref.keys() - have.keys())

    tips = []
    if missing_req:
        tips.append(f"Add evidence for required skills: {', '.join(missing_req[:6])} — a bullet with a concrete result for each, if true.")
    if missing_pref:
        tips.append(f"Nice-to-haves you could mention if you have them: {', '.join(missing_pref[:6])}.")
    if req_years and (res_years or 0) < req_years:
        tips.append(f"JD asks for {req_years}+ years; state your total years explicitly in the summary.")
    gaps = _keyword_gaps(resume, jd)
    if gaps:
        tips.append("Mirror the JD's wording where accurate (ATS keyword match): " + ", ".join(gaps[:8]) + ".")
    if not re.search(r"\d+\s*%|\$\s*\d|\d+x\b", resume):
        tips.append("Quantify impact — add numbers (%, $, time saved, scale) to your top bullets.")

    return FitReport(
        score=round(final, 1), skill_coverage=round(100 * coverage, 1), semantic_similarity=round(sim, 3),
        required_years=req_years, resume_years=res_years, matched=sorted(have.keys() & (jd_req.keys() | jd_pref.keys())),
        missing_required=missing_req, missing_preferred=missing_pref, keyword_gaps=gaps, suggestions=tips,
    )
