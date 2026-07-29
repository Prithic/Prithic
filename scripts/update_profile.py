#!/usr/bin/env python3
"""Refresh dynamic sections in the GitHub profile README."""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
USER = "Prithic"
API = f"https://api.github.com/users/{USER}/repos?type=owner&sort=updated&direction=desc&per_page=100"

LANG_SKILLS = {
    "Python": ["Python", "FastAPI", "ML experiments"],
    "TypeScript": ["TypeScript", "React", "frontend systems"],
    "JavaScript": ["JavaScript", "browser apps", "dashboards"],
    "HTML": ["HTML/CSS", "responsive UI"],
    "C++": ["C++", "embedded systems"],
    "C": ["C", "firmware fundamentals"],
    "Java": ["Java", "DSA practice"],
}

KEYWORD_SKILLS = {
    "ai": "AI systems",
    "fraud": "fraud detection",
    "surveillance": "computer vision / monitoring",
    "iot": "IoT dashboards",
    "rag": "RAG workflows",
    "robot": "robotics",
    "esp32": "ESP32",
    "education": "edtech",
    "language": "language learning tools",
}


def fetch_repos() -> list[dict]:
    req = urllib.request.Request(API, headers={"User-Agent": "Prithic-profile-updater"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def marker(name: str, body: str) -> str:
    return f"<!-- AUTO:{name}:start -->\n{body.rstrip()}\n<!-- AUTO:{name}:end -->"


def replace_marker(text: str, name: str, body: str) -> str:
    pattern = re.compile(
        rf"<!-- AUTO:{re.escape(name)}:start -->.*?<!-- AUTO:{re.escape(name)}:end -->",
        re.DOTALL,
    )
    replacement = marker(name, body)
    if pattern.search(text):
        return pattern.sub(replacement, text)
    return text.rstrip() + "\n\n" + replacement + "\n"


def repo_score(repo: dict) -> tuple:
    pushed = repo.get("pushed_at") or ""
    stars = repo.get("stargazers_count") or 0
    forks = repo.get("forks_count") or 0
    has_description = 1 if repo.get("description") else 0
    return (pushed, stars + forks, has_description)


def describe(repo: dict) -> str:
    description = repo.get("description") or "Active build from my GitHub workspace."
    description = re.sub(r"\s+", " ", description).strip()
    if len(description) > 120:
        description = description[:117].rstrip() + "..."
    language = repo.get("language") or "Mixed"
    pushed = (repo.get("pushed_at") or "")[:10]
    return (
        f"| [{repo['name']}]({repo['html_url']}) | {language} | "
        f"{description} | {pushed} |"
    )


def infer_skills(repos: list[dict]) -> list[str]:
    skills: list[str] = []
    languages = Counter(repo.get("language") for repo in repos if repo.get("language"))
    for language, _ in languages.most_common():
        skills.extend(LANG_SKILLS.get(language, [language]))

    haystack = " ".join(
        f"{repo.get('name', '')} {repo.get('description') or ''}".lower() for repo in repos
    )
    for keyword, skill in KEYWORD_SKILLS.items():
        if keyword in haystack:
            skills.append(skill)

    ordered = []
    for skill in skills:
        if skill not in ordered:
            ordered.append(skill)
    return ordered[:18]


def build_sections(repos: list[dict]) -> dict[str, str]:
    own_repos = [repo for repo in repos if not repo.get("fork") and repo["name"] != USER]
    own_repos.sort(key=repo_score, reverse=True)
    featured = own_repos[:6]
    languages = Counter(repo.get("language") for repo in own_repos if repo.get("language"))
    skills = infer_skills(own_repos)
    refreshed = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    focus_lines = [
        "- Building practical AI and web systems from public repo work, not just profile badges.",
        "- Current momentum: " + ", ".join(repo["name"] for repo in featured[:3]) + ".",
        "- Learning path: C fundamentals, embedded/ESP32 work, DSA, and production-style deployments.",
        f"- Profile intelligence refreshed automatically at **{refreshed}**.",
    ]

    featured_table = [
        "| Project | Stack signal | What it shows | Last push |",
        "| --- | --- | --- | --- |",
    ]
    featured_table.extend(describe(repo) for repo in featured)

    skill_body = [
        "**Repo-inferred skills:** " + " | ".join(skills),
        "",
        "**Language signal:** "
        + " | ".join(f"{language} ({count})" for language, count in languages.most_common(6)),
    ]

    return {
        "CURRENT_FOCUS": "\n".join(focus_lines),
        "FEATURED_PROJECTS": "\n".join(featured_table),
        "SKILL_SIGNAL": "\n".join(skill_body),
    }


def main() -> int:
    readme = README.read_text(encoding="utf-8")
    repos = fetch_repos()
    sections = build_sections(repos)
    for name, body in sections.items():
        readme = replace_marker(readme, name, body)
    README.write_text(readme, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
