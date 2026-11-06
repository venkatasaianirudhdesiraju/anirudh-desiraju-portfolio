"""Skill taxonomy: canonical name → aliases (lowercase). Extend freely."""
from __future__ import annotations

import re

SKILLS: dict[str, list[str]] = {
    # languages
    "Python": ["python", "python3"], "Java": ["java"], "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript", "ts"], "Go": ["golang", "go lang"], "Rust": ["rust"], "C++": ["c++", "cpp"],
    "C#": ["c#", "csharp", ".net"], "SQL": ["sql"], "Scala": ["scala"], "Bash": ["bash", "shell scripting"],
    "R": ["r language", "rstudio"],
    # backend
    "Flask": ["flask"], "FastAPI": ["fastapi"], "Django": ["django"], "Node.js": ["node.js", "nodejs", "node"],
    "REST APIs": ["rest", "restful", "rest api", "rest apis"], "GraphQL": ["graphql"], "gRPC": ["grpc"],
    "Microservices": ["microservices", "microservice", "service-oriented"], "Celery": ["celery"],
    "Kafka": ["kafka"], "RabbitMQ": ["rabbitmq"], "Redis": ["redis"], "Spring Boot": ["spring boot", "spring"],
    # frontend
    "React": ["react", "reactjs", "react.js"], "Next.js": ["next.js", "nextjs"], "Angular": ["angular"],
    "Vue": ["vue", "vue.js"], "HTML/CSS": ["html", "css", "html5", "css3"], "Tailwind": ["tailwind"],
    # data / ml
    "Pandas": ["pandas"], "NumPy": ["numpy"], "scikit-learn": ["scikit-learn", "sklearn"],
    "PyTorch": ["pytorch", "torch"], "TensorFlow": ["tensorflow", "keras"], "Spark": ["spark", "pyspark"],
    "Airflow": ["airflow"], "dbt": ["dbt"], "ETL": ["etl", "elt", "data pipelines", "data pipeline"],
    "NLP": ["nlp", "natural language processing", "nltk", "spacy"], "LLMs": ["llm", "llms", "large language model",
    "large language models", "genai", "generative ai", "gpt"], "RAG": ["rag", "retrieval augmented", "retrieval-augmented"],
    "LangChain": ["langchain"], "Computer Vision": ["computer vision", "opencv"], "MLOps": ["mlops", "mlflow"],
    "Machine Learning": ["machine learning", "ml"], "Statistics": ["statistics", "statistical"],
    "Snowflake": ["snowflake"], "Databricks": ["databricks"], "Tableau": ["tableau"], "Power BI": ["power bi"],
    # databases
    "PostgreSQL": ["postgresql", "postgres"], "MySQL": ["mysql"], "MongoDB": ["mongodb", "mongo"],
    "Oracle": ["oracle", "pl/sql", "plsql"], "DynamoDB": ["dynamodb"], "Elasticsearch": ["elasticsearch", "opensearch"],
    # cloud / devops
    "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda", "rds"], "Azure": ["azure"], "GCP": ["gcp", "google cloud"],
    "Docker": ["docker", "containers", "containerization"], "Kubernetes": ["kubernetes", "k8s", "eks", "aks", "gke"],
    "Terraform": ["terraform", "infrastructure as code", "iac"], "CI/CD": ["ci/cd", "cicd", "continuous integration",
    "jenkins", "github actions", "gitlab ci", "azure devops"], "Linux": ["linux", "unix"], "Git": ["git", "github", "gitlab"],
    "Observability": ["observability", "prometheus", "grafana", "datadog", "splunk"],
    # testing / process
    "Selenium": ["selenium", "webdriver"], "Pytest": ["pytest"], "Unit Testing": ["unit testing", "unittest", "tdd",
    "test automation", "automated testing"], "Agile": ["agile", "scrum", "kanban"], "JIRA": ["jira"],
    "System Design": ["system design", "distributed systems", "scalability"], "Security": ["oauth", "owasp", "security"],
}

_PATTERNS = {
    canon: re.compile(r"(?<![\w+#.])(?:" + "|".join(re.escape(a) for a in sorted(al, key=len, reverse=True)) + r")(?![\w+#])", re.I)
    for canon, al in SKILLS.items()
}
# Words that are aliases but too ambiguous unless written in a skills context.
_AMBIGUOUS = {"Go": None, "R": None, "Node.js": re.compile(r"\bnode\b(?!\.js)", re.I)}


def find_skills(text: str) -> dict[str, int]:
    """Canonical skill → number of mentions."""
    found = {}
    for canon, pat in _PATTERNS.items():
        hits = pat.findall(text)
        if canon == "Node.js":  # bare "node" only counts alongside JS context
            hits = [h for h in hits if h.lower() != "node"] or (hits if re.search(r"javascript|npm|express", text, re.I) else [])
        if hits:
            found[canon] = len(hits)
    return found
