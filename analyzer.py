"""Explainable, local resume-to-job analysis. No personal attributes are used."""
from __future__ import annotations

import math
import re
from collections import Counter

SKILL_ALIASES = {
    "python": ["python"], "javascript": ["javascript", "js"], "typescript": ["typescript", "ts"],
    "java": ["java"], "c#": ["c#", "c sharp", "csharp"], "c++": ["c++"], "sql": ["sql"],
    "html": ["html", "html5"], "css": ["css", "css3"], "react": ["react", "reactjs", "react.js"],
    "node.js": ["node", "nodejs", "node.js"], "next.js": ["next.js", "nextjs"], "angular": ["angular"],
    "vue": ["vue", "vue.js", "vuejs"], "fastapi": ["fastapi"], "django": ["django"], "flask": ["flask"],
    "spring boot": ["spring boot"], "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"], "nlp": ["nlp", "natural language processing"],
    "data analysis": ["data analysis", "data analytics"], "pandas": ["pandas"], "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"], "tensorflow": ["tensorflow"], "pytorch": ["pytorch"],
    "docker": ["docker", "containerization"], "kubernetes": ["kubernetes", "k8s"], "aws": ["aws", "amazon web services"],
    "azure": ["azure"], "gcp": ["gcp", "google cloud platform"], "git": ["git", "github", "gitlab"],
    "ci/cd": ["ci/cd", "continuous integration", "continuous deployment"], "linux": ["linux"],
    "postgresql": ["postgresql", "postgres"], "mysql": ["mysql"], "mongodb": ["mongodb"],
    "redis": ["redis"], "rest api": ["rest api", "restful", "rest APIs"], "graphql": ["graphql"],
    "figma": ["figma"], "tableau": ["tableau"], "power bi": ["power bi", "powerbi"],
    "spark": ["apache spark", "pyspark", "spark"], "airflow": ["airflow", "apache airflow"],
    "agile": ["agile", "scrum", "kanban"], "testing": ["unit testing", "integration testing", "testing"],
    "security": ["cybersecurity", "application security", "security"], "microservices": ["microservices", "microservice"],
}
STOPWORDS = {"the", "and", "for", "with", "that", "this", "from", "your", "are", "you", "our", "will", "have", "has", "into", "their", "who", "job", "role", "work", "years", "year", "experience", "skills", "a", "an", "of", "in", "to", "on", "is", "as", "be", "or", "at", "by"}


def _contains(text: str, phrase: str) -> bool:
    # Technical tokens can include +, #, and dots; only letters/digits should
    # prevent a boundary. This also lets "ReactJS." match at sentence end.
    return bool(re.search(r"(?<![a-z0-9])" + re.escape(phrase.lower()) + r"(?![a-z0-9])", text.lower()))


def extract_skills(text: str) -> list[str]:
    return sorted(skill for skill, aliases in SKILL_ALIASES.items() if any(_contains(text, alias) for alias in aliases))


def _tokens(text: str) -> Counter:
    words = re.findall(r"[a-z][a-z0-9+#.]{1,}", text.lower())
    return Counter(word for word in words if word not in STOPWORDS)


def cosine_relevance(first: str, second: str) -> int:
    one, two = _tokens(first), _tokens(second)
    shared = set(one) & set(two)
    numerator = sum(one[word] * two[word] for word in shared)
    denominator = math.sqrt(sum(value * value for value in one.values())) * math.sqrt(sum(value * value for value in two.values()))
    return round(100 * numerator / denominator) if denominator else 0


def quality_checks(resume: str) -> tuple[int, list[dict]]:
    lower = resume.lower()
    checks = [
        ("Contact details", bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+|\+?\d[\d\s()-]{7,}", resume))),
        ("Experience or projects", any(term in lower for term in ("experience", "projects", "project", "employment"))),
        ("Education", "education" in lower or "university" in lower or "degree" in lower),
        ("Skills section", "skills" in lower or "technologies" in lower),
        ("Measurable impact", bool(re.search(r"\b\d+(?:%|\+|x| users|ms| hours)\b", lower))),
    ]
    return round(100 * sum(passed for _, passed in checks) / len(checks)), [{"label": label, "passed": passed} for label, passed in checks]


def analyze(resume: str, job: str) -> dict:
    resume_skills, job_skills = extract_skills(resume), extract_skills(job)
    matching = sorted(set(resume_skills) & set(job_skills))
    missing = sorted(set(job_skills) - set(resume_skills))
    relevance = cosine_relevance(resume, job)
    coverage = round(100 * len(matching) / len(job_skills)) if job_skills else 0
    quality, checks = quality_checks(resume)
    score = round(relevance * .6 + coverage * .3 + quality * .1)
    suggestions = []
    if missing:
        suggestions.append({"title": "Address genuine skill gaps", "detail": f"If you have used them, make evidence for {', '.join(missing[:4])} easy to find. Otherwise, prioritize learning the most relevant gaps - do not add skills you do not have."})
    if not any(item["passed"] and item["label"] == "Measurable impact" for item in checks):
        suggestions.append({"title": "Add evidence, not adjectives", "detail": "Where truthful, describe scope, outcomes, performance, time saved, or users supported in your projects and experience."})
    if relevance < 45:
        suggestions.append({"title": "Tailor the summary", "detail": "Reflect the role's real responsibilities in your summary and project descriptions, using clear wording backed by your actual work."})
    if not suggestions:
        suggestions.append({"title": "Keep the evidence prominent", "detail": "Your resume aligns well on the detected signals. Lead with the projects and outcomes most relevant to this role."})
    return {"score": score, "components": {"relevance": relevance, "coverage": coverage, "quality": quality}, "resume_skills": resume_skills, "job_skills": job_skills, "matching_skills": matching, "missing_skills": missing, "checks": checks, "suggestions": suggestions, "disclaimer": "This is an explainable compatibility estimate for career guidance, not an ATS score or a hiring decision."}
