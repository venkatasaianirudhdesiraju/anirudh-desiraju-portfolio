"""Starter plan, tailored to: senior Python dev (6 yrs, GE Healthcare / Intel), wants more income, a stronger resume,
better health and habits, publishing, YouTube. Everything is editable in the dashboard. Money/card values start
empty — you enter your own (they never leave your computer)."""
from __future__ import annotations

BOOKS = [
    # reading now — small daily targets that compound (≈ 12 pages/day → ~15 books/year)
    ("The Psychology of Money", "Morgan Housel", "How people actually build wealth: behavior > intelligence. Fastest money-mindset upgrade.", "Money", 256, 5, "reading"),
    ("Atomic Habits", "James Clear", "The operating system for every other goal here: tiny daily systems.", "Mindset", 320, 3, "reading"),
    ("Designing Data-Intensive Applications", "Martin Kleppmann", "The book senior/staff backend interviews draw from. Directly raises your pay band.", "Career/Tech", 616, 2, "reading"),
    ("How to Win Friends and Influence People", "Dale Carnegie", "Charisma and likability fundamentals, at work and in dating.", "People", 288, 2, "reading"),
    # queue — in a deliberate order
    ("The Simple Path to Wealth", "JL Collins", "Simple index-fund investing. Read before trading individual stocks.", "Money", 286, 5, "queued"),
    ("Deep Work", "Cal Newport", "Focus as a career advantage. Ship more side projects in fewer hours.", "Mindset", 296, 5, "queued"),
    ("System Design Interview Vol. 1", "Alex Xu", "Practical interview prep that pairs with Kleppmann.", "Career/Tech", 322, 3, "queued"),
    ("Never Split the Difference", "Chris Voss", "Negotiating salary, freelance rates and everything else.", "People", 288, 5, "queued"),
    ("$100M Offers", "Alex Hormozi", "How to package a service people pay for. Use it for freelancing and the API products.", "Business", 160, 5, "queued"),
    ("Show Your Work!", "Austin Kleon", "Build in public: GitHub, YouTube and your portfolio as an audience.", "Business", 224, 10, "queued"),
    ("The Almanack of Naval Ravikant", "Eric Jorgenson", "Leverage, specific knowledge and long-term games.", "Mindset", 242, 5, "queued"),
    ("Influence", "Robert Cialdini", "The psychology of persuasion, useful for sales, content and life.", "People", 336, 4, "queued"),
    ("Why We Sleep", "Matthew Walker", "Sleep is the cheapest performance enhancer you can get.", "Health", 368, 5, "queued"),
    ("The Intelligent Investor", "Benjamin Graham", "Margin of safety. Read before you trust any trading bot.", "Money", 640, 3, "queued"),
    ("Can't Hurt Me", "David Goggins", "Mental toughness and discipline when motivation runs out.", "Mindset", 364, 5, "queued"),
]

WORKOUTS = [  # beginner full-body 3x/week + daily walking. Progress: add a rep or a little weight each week.
    ("Mon", "Full body A", "Goblet squat 3×10 · Push-ups (incline if needed) 3×8–12 · Dumbbell row 3×10/side · Plank 3×30s · 10-min walk", 45),
    ("Tue", "Walk + mobility", "30–40 min brisk walk (~8k steps) · 10 min mobility: hips, thoracic spine, hamstrings", 45),
    ("Wed", "Full body B", "Romanian deadlift 3×10 · Dumbbell overhead press 3×10 · Lat pulldown or band pull-apart 3×12 · Dead bug 3×10", 45),
    ("Thu", "Walk + posture", "30–40 min walk · Desk-posture set: chin tucks, wall angels, glute bridges 3×15", 45),
    ("Fri", "Full body A+", "Same as Monday, with one more rep or a bit more weight than last time · Farmer carry 3×40m", 50),
    ("Sat", "Cardio you enjoy", "45–60 min: hike, swim, bike, sport or Zone-2 jog (you can still talk in full sentences)", 60),
    ("Sun", "Rest + plan", "Easy walk · Weekly review in LifeOS: money, tasks, reading, plan next week", 20),
]

TASKS = [
    ("Push all projects in 'ai code/projects' to GitHub with good READMEs", "Career", "P1", "todo"),
    ("Deploy the portfolio to Vercel and put the link on your resume and LinkedIn", "Career", "P1", "todo"),
    ("Paper-trade TradeScout every weekday for 6 weeks before using any real money", "Money", "P1", "doing"),
    ("Enter every credit card in LifeOS (balance, limit, APR, due day)", "Money", "P1", "todo"),
    ("Import last 3 months of card/bank transactions (CSV) into Purchases", "Money", "P2", "todo"),
    ("Set up automatic transfers: emergency fund → then index funds", "Money", "P1", "todo"),
    ("Record YouTube video #1: 'I built an AI that triages failed tests'", "YouTube", "P2", "todo"),
    ("Create an Upwork / Toptal profile focused on Python automation + data pipelines", "Money", "P2", "todo"),
    ("Write the LogLens blog post / arXiv draft outline", "Research", "P2", "todo"),
    ("Book an annual physical + blood work", "Life", "P2", "todo"),
    ("Update LinkedIn headline: 'Senior Python Engineer · Data/ML pipelines · Local AI tooling'", "Career", "P1", "todo"),
]

RISKS = [
    ("High-interest credit card debt", "Money", 4, 4, "Avalanche payoff: pay minimums everywhere and every extra dollar to the highest APR. Don't add new 'want' spending to cards. Ask each issuer for a lower APR, or use a 0% balance transfer if it's cheaper after the fee.", "open"),
    ("No emergency fund", "Money", 3, 5, "Automate $X per paycheck into high-yield savings until it covers 1 month of expenses, then 3–6 months. Do this before investing beyond your 401(k) match.", "open"),
    ("Losing money trading", "Money", 4, 4, "Paper-trade 6+ weeks. Risk at most 1% per trade, with a hard stop. Keep trading money under 5–10% of net worth and the rest in index funds.", "open"),
    ("Single income source / layoffs", "Career", 3, 5, "Keep the resume and portfolio current, interview at least once a quarter, build one freelance or product income stream, and keep 6 months of runway.", "open"),
    ("Skills going stale (AI shift)", "Career", 3, 4, "Ship one AI/LLM project per quarter (local LLMs, RAG, agents), finish DDIA + System Design, and publish what you learn.", "mitigating"),
    ("Sedentary desk job → health decline", "Health", 4, 4, "8k steps a day, strength training 3×/week, 7–8h sleep, standing breaks every hour, yearly blood work.", "open"),
    ("Burnout from too many projects", "Life", 3, 3, "At most 2 side projects active at once. Weekly review on Sunday. Drop or park anything not moving a goal.", "open"),
    ("No insurance / estate basics", "Legal", 2, 5, "Check your health, disability and renters insurance. Add beneficiaries to your 401(k) and brokerage accounts.", "open"),
]

INCOME = [
    ("Freelance Python automation & data pipelines (Upwork/Toptal/referrals)", 3000, "medium", "Create a profile with 3 portfolio pieces (LogLens, DataGuard, JobFit). Bid on 5 jobs a week at $60–90/hr.", "idea"),
    ("Sell LogLens as a hosted API / GitHub Action for QA teams", 1500, "high", "Put it behind apisaas, write a landing page, post to r/QualityAssurance and LinkedIn, and offer 3 free pilots.", "idea"),
    ("JobFit resume-optimizer micro-SaaS", 800, "medium", "Launch the free web version, collect 50 users, then charge $9/month for unlimited tailoring.", "idea"),
    ("YouTube: Python + local AI builds", 500, "high", "Publish 1 video a week for 6 months. Money comes from sponsors, affiliates and leads for consulting.", "idea"),
    ("Resume/portfolio reviews for engineers", 600, "low", "Offer $49 reviews using JobFit + your experience. Post on LinkedIn.", "idea"),
    ("Paid internal-tools consulting for medical-device / hardware validation teams", 4000, "high", "Package your GE/Intel experience as a 'V&V automation audit'. Check your employment contract for conflicts first.", "idea"),
    ("Index-fund investing (long-term compounding)", 0, "low", "Automate monthly contributions. Boring and the most reliable wealth builder.", "testing"),
]

YOUTUBE = [
    ("Build With Anirudh", "I built an AI that finds why your tests fail", "Show 300 failed tests collapsing into 4 root causes in 2 seconds.", "idea"),
    ("Build With Anirudh", "I trained a stock-picking model from scratch. Here's the honest result", "Most AI trading videos lie. Here's what out-of-sample testing really shows.", "idea"),
    ("Build With Anirudh", "Run ChatGPT-style AI on your own PC (Ollama, 10 minutes)", "Free, private, offline AI. Set it up live.", "idea"),
    ("Build With Anirudh", "My resume scored 61%. I fixed it to 90% with Python", "A before/after ATS score using a tool I built.", "idea"),
    ("Build With Anirudh", "Senior Python dev reviews beginner projects", "A series format: viewers submit their repos.", "idea"),
]

RESEARCH = [
    ("LLM-assisted root-cause triage of test failures", "How much triage time do clustering + a local LLM save vs manual triage, and how accurate is it?",
     "Collect labeled failure logs (public CI data, e.g. GitHub Actions of OSS projects). Compare TF-IDF clustering, embeddings, and an LLM. Measure precision/recall of root-cause grouping and time saved.",
     "arXiv (cs.SE) → ICST / ASE workshop; also a blog post"),
    ("Calibration of ML trading signals for retail investors", "Do common retail 'AI stock picker' signals survive walk-forward validation and costs?",
     "Use TradeScout's walk-forward framework on 10 years of data. Report AUC, calibration and post-cost Sharpe; compare with baselines; publish code.",
     "arXiv (q-fin.TR) or SSRN; Medium/dev.to write-up"),
    ("Privacy-preserving resume–job matching with local LLMs", "Can a local 8B model match cloud LLMs at resume tailoring without sending personal data out?",
     "Build a benchmark of resume/JD pairs. Compare keyword, embedding and LLM scoring against human ratings.", "arXiv (cs.CL/cs.IR); a portfolio case study"),
    ("Data-quality gates in regulated (FDA) software pipelines", "What lightweight validation catches the most defects in medical-device data pipelines?",
     "Write a case study of DataGuard-style rules (anonymized). Classify defects and measure catch rates.", "IEEE Software / industry blog (get employer approval)"),
]

GOALS = [
    ("Pay off all credit card debt", "Money", 100, 0, "% paid", ""),
    ("Emergency fund", "Money", 6, 0, "months of expenses", ""),
    ("Pages read this year", "Learning", 4000, 0, "pages", ""),
    ("Side income per month", "Money", 2000, 0, "$", ""),
    ("YouTube videos published", "YouTube", 24, 0, "videos", ""),
    ("Strength workouts this quarter", "Health", 36, 0, "workouts", ""),
    ("Papers / technical posts published", "Research", 2, 0, "pieces", ""),
]


def seed(store) -> bool:
    """Seed only an empty database."""
    if store.count("books") or store.count("tasks"):
        return False
    for t, a, why, cat, total, daily, st in BOOKS:
        store.add("books", dict(title=t, author=a, why=why, category=cat, total_pages=total, pages_read=0, daily_pages=daily, status=st))
    for d, n, det, m in WORKOUTS:
        store.add("workouts", dict(day=d, name=n, details=det, minutes=m))
    for t, area, p, st in TASKS:
        store.add("tasks", dict(title=t, area=area, priority=p, status=st, due="", notes=""))
    for r, area, l, i, mit, st in RISKS:
        store.add("risks", dict(risk=r, area=area, likelihood=l, impact=i, mitigation=mit, status=st))
    for idea, pot, eff, step, st in INCOME:
        store.add("income", dict(idea=idea, monthly_potential=pot, effort=eff, first_step=step, status=st, earned_to_date=0))
    for ch, title, hook, st in YOUTUBE:
        store.add("youtube", dict(channel=ch, video_title=title, hook=hook, status=st, publish_date="", views=0))
    for topic, q, m, v in RESEARCH:
        store.add("research", dict(topic=topic, question=q, method=m, venue=v, status="idea"))
    for g, area, tgt, cur, unit, dl in GOALS:
        store.add("goals", dict(goal=g, area=area, target=tgt, current=cur, unit=unit, deadline=dl))
    return True
