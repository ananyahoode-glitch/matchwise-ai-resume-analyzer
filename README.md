# Matchwise - AI Resume Analyzer

A privacy-first, explainable resume-to-job matching app. Matchwise helps job seekers understand alignment with a role; it is **not** an automated hiring system or an ATS score.


## Features

- Upload PDF, DOCX, or TXT resumes, or paste resume text
- Extracts and normalizes 70+ technology and professional skills
- Combines lexical relevance, required-skill coverage, and resume-quality checks
- Presents a transparent scoring breakdown, matching skills, skill gaps, and evidence-based suggestions
- Never invents qualifications and avoids sensitive personal attributes
- Runs locally with no database, telemetry, or resume retention

## Quick start

```bash
python server.py
```

Then open [http://localhost:8000](http://localhost:8000). Python 3.10+ is required. PDF and DOCX extraction work automatically when `pypdf` and `python-docx` are installed:

```bash
pip install -r requirements.txt
```

## Test

```bash
python -m unittest discover -s tests -v
```

## How the score works

`overall = 60% text relevance + 30% required-skill coverage + 10% resume-quality checks`

Text relevance is cosine similarity of normalized term-frequency vectors (a local, transparent baseline). Skill coverage compares the job's discovered skills against the resume's discovered skills. Quality checks look for standard resume sections and evidence-oriented writing. The result is an assistive compatibility estimate, never a likelihood of being hired.

## Project structure

```text
matchwise/
├── server.py              # Standard-library HTTP API and static server
├── src/
│   ├── analyzer.py        # Scoring, skill extraction, suggestions
│   └── document_parser.py # PDF/DOCX/TXT parsing
├── static/                # Responsive frontend
├── tests/                 # Unit tests
└── requirements.txt       # Optional format parsers
```


