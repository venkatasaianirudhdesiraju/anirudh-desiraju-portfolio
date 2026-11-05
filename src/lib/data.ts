export const profile = {
  name: "Anirudh Desiraju",
  shortName: "Anirudh",
  initials: "AD",
  title: "Senior Python Developer",
  subtitle: "Backend systems, data/ML pipelines & cloud infrastructure",
  summary:
    "Senior Python developer with 6+ years building production APIs, data/ML pipelines, and cloud-native automation. I work across Flask/FastAPI backends, AWS infrastructure, and data engineering (Pandas, NumPy, scikit-learn, Spark) — with hands-on React on the front end when a feature needs a face. Recent work spans regulated medical-device engineering at GE Healthcare and pre-silicon GPU validation at Intel.",
  location: "Folsom / Sacramento, CA",
  email: "desirajuanirudh.py@gmail.com",
  phone: "+1 (916) 827-7411",
  linkedin: "https://www.linkedin.com/in/anirudhdesiraju/",
  github: "https://github.com/pewdiepie-archdaemon",
  resumeHref: "/resume.pdf",
  yearsExperience: 6,
  certifications: ["AWS Certified Developer – Associate"],
  education: {
    degree: "M.S. in Computer Science",
    school: "California State University, Sacramento",
  },
} as const;

export type Experience = {
  company: string;
  role: string;
  location: string;
  period: string;
  current?: boolean;
  summary: string;
  highlights: string[];
  stack: string[];
};

export const experience: Experience[] = [
  {
    company: "GE Healthcare",
    role: "Python Developer",
    location: "Waukesha, WI",
    period: "Sep 2025 — Present",
    current: true,
    summary:
      "Engineering automation for CT data acquisition, validation, and testing in a regulated medical-device environment.",
    highlights: [
      "Designed Python automation workflows spanning CT data acquisition, integration, validation, and testing — cutting manual execution across engineering processes.",
      "Built Pandas ETL pipelines to ingest, transform, enrich, and validate CT acquisition datasets with schema enforcement and automated quality checks.",
      "Automated CT system validation and regression testing, including phantom-based acquisition, calibration verification, and performance checks.",
      "Integrated services with ALM, JIRA, and JAMA-style systems to automate requirements traceability and audit-ready test matrices for V&V stakeholders.",
      "Shipped internal engineering dashboards in React to visualize test results, workflow status, and operational metrics.",
    ],
    stack: ["Python", "Flask", "AWS", "Oracle ATP", "MongoDB", "React", "Pandas", "Selenium"],
  },
  {
    company: "Intel",
    role: "Python Developer",
    location: "Folsom, CA",
    period: "Nov 2021 — Aug 2025",
    summary:
      "Pre-silicon GPU validation tooling and NLP pipelines for display-interface verification.",
    highlights: [
      "Supported pre-silicon GPU validation and hardware modeling for display interfaces (DP/eDP/HDMI) with Python verification tooling.",
      "Led Python 3.x upgrades and dependency compatibility fixes across automation suites, prioritizing scalability and maintainability.",
      "Built NLP pipelines (NLTK, scikit-learn, TF-IDF, cosine similarity) for text classification and clustering, exposed via Flask REST endpoints.",
      "Engineered text-processing and vectorization stages — tokenization, preprocessing, feature extraction — for structured and unstructured datasets.",
      "Implemented Selenium/WebDriver compatibility and cross-browser test suites against dynamic and static DOM behavior.",
    ],
    stack: ["Python", "Flask", "AWS", "NLTK", "scikit-learn", "ReactJS", "Java", "Selenium"],
  },
  {
    company: "Savitude",
    role: "Python Developer — Fashion Dashboard",
    location: "Palo Alto, CA",
    period: "Jan 2021 — Oct 2021",
    summary:
      "ML-driven garment placement prediction served through a Flask/React dashboard.",
    highlights: [
      "Trained and served ML models to predict garment pixel positions on a mannequin figure, operationalized as inference on AWS Lambda.",
      "Implemented a service-oriented architecture with Flask backends and React/HTML/CSS frontends, with API versioning and validation.",
      "Built Selenium regression suites integrated with the API test framework to catch UI/contract drift early.",
      "Wrote Oracle PL/SQL procedures and triggers for reporting logic; used Flask ORM for data access across PostgreSQL/MySQL.",
    ],
    stack: ["Python", "Flask", "AWS Lambda", "React", "PostgreSQL", "Oracle PL/SQL", "Pandas"],
  },
  {
    company: "Stamp It Biz",
    role: "Full Stack Developer Intern",
    location: "Hyderabad, India",
    period: "Jan 2018 — Aug 2018",
    summary: "MVC internal web services and CI foundations, early career.",
    highlights: [
      "Implemented MVC with Flask and RESTful APIs for internal services across the full SDLC in an Agile team.",
      "Owned database integration and tuning, applying ORM patterns and optimizing Oracle stored procedures.",
      "Established CI with Jenkins and source control with GitHub; added automated Selenium and unit test coverage.",
    ],
    stack: ["Python", "Flask", "Node.js", "Oracle", "Jenkins", "SaltStack"],
  },
];

export type Project = {
  name: string;
  tagline: string;
  description: string;
  stack: string[];
  href?: string;
  image?: string;
  featured?: boolean;
  stats?: { label: string; value: string }[];
};

export const flagshipProject: Project = {
  name: "Odysseus",
  tagline: "A self-hosted AI workspace — chat, agents, research, documents, email, and local models.",
  description:
    "Odysseus is an open-source, self-hosted workspace that brings chat, autonomous agents, deep research, a writing-first document editor, email triage, notes/tasks/calendar, and local model serving into one app. It runs fully on your own hardware via Docker, with hardware-aware model recommendations and MCP/tool support for agents that can use files, shell, and skills. Built and maintained as an active multi-contributor open-source project.",
  stack: ["Python", "Docker", "MCP", "Local LLMs (Ollama)", "React", "IMAP/SMTP", "CalDAV"],
  href: "https://github.com/pewdiepie-archdaemon/odysseus",
  image: "/images/odysseus-browser.jpg",
  featured: true,
  stats: [
    { label: "commits authored", value: "420+" },
    { label: "contributors", value: "10+" },
    { label: "core features", value: "8" },
  ],
};

export const projects: Project[] = [
  {
    name: "Acquisition-to-Test Orchestrator",
    tagline: "Pipelines + testing automation",
    description:
      "Python pipeline that automates the path from data acquisition to test execution — validation, schema enforcement, and traceability-artifact generation, wired into source control and CI/CD for repeatable releases.",
    stack: ["Python", "CI/CD", "Schema Validation", "Jenkins"],
  },
  {
    name: "AI-Driven Test Failure Root Cause Analyzer",
    tagline: "Enterprise GenAI tooling",
    description:
      "An enterprise analysis tool that applies GenAI to triage test failures — surfacing likely root causes from logs and historical failure patterns to cut manual investigation time for engineering and V&V teams.",
    stack: ["Python", "GenAI", "NLP", "Enterprise Integration"],
  },
  {
    name: "Keyboard Logger",
    tagline: "Low-level input instrumentation",
    description:
      "A lightweight, low-level keyboard event logger built for local diagnostics and automation testing workflows.",
    stack: ["Python", "Systems Programming"],
  },
];

export type SkillGroup = { category: string; skills: string[] };

export const skills: SkillGroup[] = [
  {
    category: "Backend & APIs",
    skills: ["Python", "Flask", "FastAPI", "REST APIs", "MVC", "Node.js"],
  },
  {
    category: "Web",
    skills: ["React", "JavaScript", "TypeScript", "HTML5", "CSS3", "jQuery"],
  },
  {
    category: "Cloud & Infra",
    skills: ["AWS (EC2, S3, RDS, Lambda, API Gateway, ELB)", "Azure", "Docker", "Kubernetes"],
  },
  {
    category: "Data & ML",
    skills: ["Pandas", "NumPy", "scikit-learn", "OpenCV", "Spark", "NLP (NLTK, TF-IDF)"],
  },
  {
    category: "Databases",
    skills: ["PostgreSQL", "MySQL", "Oracle / PL-SQL", "MongoDB"],
  },
  {
    category: "DevOps & QA",
    skills: ["Git", "Jenkins", "GitHub Actions", "Azure DevOps", "Selenium", "Unittest", "JIRA"],
  },
];

export const navLinks = [
  { href: "#about", label: "About" },
  { href: "#experience", label: "Experience" },
  { href: "#work", label: "Work" },
  { href: "#skills", label: "Skills" },
  { href: "#contact", label: "Contact" },
];
