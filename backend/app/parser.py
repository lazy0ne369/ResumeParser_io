from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Iterable

from docx import Document
from PyPDF2 import PdfReader


SKILL_CATALOG: dict[str, list[str]] = {
    "languages": [
        "python",
        "java",
        "javascript",
        "typescript",
        "c",
        "c++",
        "c#",
        "go",
        "ruby",
        "php",
        "sql",
        "r",
    ],
    "frameworks": [
        "react",
        "next.js",
        "node.js",
        "express",
        "fastapi",
        "django",
        "flask",
        "spring boot",
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "pandas",
        "numpy",
        "tailwind css",
        "bootstrap",
        "langchain",
        "langgraph",
    ],
    "data_ai": [
        "nlp",
        "natural language processing",
        "machine learning",
        "deep learning",
        "data analysis",
        "data science",
        "computer vision",
        "llm",
        "transformers",
        "spacy",
        "nltk",
        "openai",
        "prompt engineering",
        "rag",
        "llama",
        "groq",
    ],
    "cloud_devops": [
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "terraform",
        "github actions",
        "gitlab ci",
        "vercel",
        "netlify",
        "render",
        "copilot",
    ],
    "tools": [
        "git",
        "github",
        "postman",
        "jira",
        "figma",
        "linux",
        "mongodb",
        "postgresql",
        "mysql",
        "redis",
        "firebase",
        "canva",
        "vscode",
    ],
    "soft_skills": [
        "leadership",
        "communication",
        "mentoring",
        "collaboration",
        "problem solving",
        "stakeholder management",
        "teamwork",
        "analytical thinking",
        "creative thinking",
        "adaptable",
    ],
}

SECTION_ALIASES: dict[str, set[str]] = {
    "summary": {
        "summary",
        "professional summary",
        "profile",
        "objective",
        "career objective",
    },
    "education": {"education", "academic background", "qualification", "qualifications"},
    "skills": {"skills", "technical skills", "core competencies", "competencies"},
    "projects": {"projects", "project experience", "personal projects", "academic projects"},
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "internship",
        "internships",
        "experience hackathons",
        "experience and hackathons",
        "hackathons",
    },
    "achievements": {
        "certifications and achievements",
        "certifications",
        "achievements",
        "awards",
        "honors",
    },
    "additional": {"additional information", "additional details", "additional"},
}

SECTION_TITLES = {
    "summary": "Summary",
    "education": "Education",
    "skills": "Technical Skills",
    "projects": "Projects",
    "experience": "Experience",
    "achievements": "Certifications and Achievements",
    "additional": "Additional Information",
}

ROLE_HINTS = (
    "engineer",
    "developer",
    "scientist",
    "analyst",
    "manager",
    "designer",
    "consultant",
    "specialist",
    "intern",
    "architect",
    "student",
)

MONTH_PATTERN = (
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)"
    r"[a-z]*\.?\s+\d{4}"
)
DATE_RANGE_PATTERN = re.compile(
    rf"({MONTH_PATTERN}|\d{{2}}/\d{{4}}|\d{{4}})\s*(?:-|to|–|â€“)\s*"
    rf"({MONTH_PATTERN}|\d{{2}}/\d{{4}}|\d{{4}}|present|current)",
    re.IGNORECASE,
)
EMAIL_PATTERN = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
PHONE_PATTERN = re.compile(
    r"(?:(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4})"
)
URL_PATTERN = re.compile(r"https?://[^\s]+", re.IGNORECASE)
PLAIN_LINK_PATTERN = re.compile(
    r"\b(?:linkedin\.com/[^\s|]+|github\.com/[^\s|]+|leetcode\.com/[^\s|]+|codechef\.com/[^\s|]+)\b",
    re.IGNORECASE,
)
STATUS_PATTERN = re.compile(r"\((learning|practicing|in progress|ongoing)\)", re.IGNORECASE)
LINE_PREFIX_GARBAGE = re.compile(r"^[^\w]+")


@dataclass
class ResumeDocument:
    text: str
    filename: str | None = None


def extract_text_from_bytes(filename: str, raw_bytes: bytes) -> str:
    suffix = filename.lower().rsplit(".", maxsplit=1)[-1] if "." in filename else ""

    if suffix == "pdf":
        reader = PdfReader(BytesIO(raw_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    if suffix == "docx":
        document = Document(BytesIO(raw_bytes))
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()

    return raw_bytes.decode("utf-8", errors="ignore").strip()


def parse_resume(document: ResumeDocument) -> dict[str, object]:
    cleaned_text = _normalize_text(document.text)
    lines = _non_empty_lines(cleaned_text)
    header_lines, section_blocks = _extract_section_blocks(lines)
    raw_sections = {
        block["key"]: "\n".join(_display_line(line) for line in block["lines"]).strip()
        for block in section_blocks
    }
    structured_sections = [_structure_section(block) for block in section_blocks]
    skill_groups = _extract_skill_groups_from_sections(structured_sections)
    learning_signals = _collect_learning_signals(structured_sections)
    skill_buckets = _extract_skill_buckets(cleaned_text)
    top_skills = _top_skills(skill_buckets, skill_groups)
    experience_timeline = _extract_experience_timeline(structured_sections)
    profile = _extract_contact(header_lines, lines, cleaned_text)
    education_level = _education_level(cleaned_text)
    project_entries = _find_structured_entries(structured_sections, "projects")

    return {
        "metadata": {
            "filename": document.filename,
            "characters": len(cleaned_text),
            "lineCount": len(lines),
            "sectionCount": len(section_blocks),
            "parsedAt": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
        "profile": profile,
        "highlights": {
            "topSkills": top_skills[:10],
            "educationLevel": education_level,
            "estimatedExperienceYears": _estimate_experience_years(cleaned_text, experience_timeline),
            "projectMentions": len(project_entries),
            "learningSignals": len(learning_signals),
        },
        "sections": raw_sections,
        "structuredSections": structured_sections,
        "skillBuckets": skill_buckets,
        "experienceTimeline": experience_timeline,
        "learningSignals": learning_signals,
        "insights": _build_insights(profile, top_skills, structured_sections, learning_signals),
    }


def _normalize_text(text: str) -> str:
    normalized = text.replace("\r", "\n")
    for source, target in (
        ("\u2022", "\u2022"),
        ("\u2013", "\u2013"),
        ("\u2014", "\u2014"),
        ("\u2212", "-"),
        ("\u2642", ""),
        ("\u2322", ""),
        ("\uf0b7", "\u2022"),
        ("â€¢", "\u2022"),
        ("â€“", "\u2013"),
        ("â€”", "\u2014"),
    ):
        normalized = normalized.replace(source, target)

    normalized = re.sub(r"/envel[a-z]{0,2}", " ", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"(?i)/linkedin(?=linkedin\.com/)", " ", normalized)
    normalized = re.sub(r"(?i)/github(?=github\.com/)", " ", normalized)
    normalized = re.sub(r"/linkedin", " linkedin.com/", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"/github", " github.com/", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"(?i)\blinkedinlinkedin\.com/", "linkedin.com/", normalized)
    normalized = re.sub(r"(?i)\bgithubgithub\.com/", "github.com/", normalized)
    normalized = re.sub(r"(?i)\bphone", "phone ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    return normalized.strip()


def _non_empty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _slug(line: str) -> str:
    return re.sub(r"[^a-z]+", " ", line.lower()).strip()


def _display_line(line: str) -> str:
    stripped = line.strip(" |")
    if stripped.startswith("\u2022"):
        tail = LINE_PREFIX_GARBAGE.sub("", stripped[1:]).strip()
        return f"\u2022 {tail}".strip()
    return LINE_PREFIX_GARBAGE.sub("", stripped).strip(" |")


def _extract_section_blocks(lines: list[str]) -> tuple[list[str], list[dict[str, object]]]:
    blocks: list[dict[str, object]] = []
    header_lines: list[str] = []
    current_block: dict[str, object] | None = None

    for line in lines:
        heading_key = _match_section_heading(line)
        if heading_key:
            current_block = {"key": heading_key, "title": SECTION_TITLES[heading_key], "lines": []}
            blocks.append(current_block)
            continue

        if current_block is None:
            header_lines.append(line)
            continue

        current_block["lines"].append(line)

    return header_lines, blocks


def _match_section_heading(line: str) -> str | None:
    normalized = _slug(_display_line(line))
    for key, aliases in SECTION_ALIASES.items():
        if normalized in aliases:
            return key
    return None


def _structure_section(block: dict[str, object]) -> dict[str, object]:
    key = str(block["key"])
    title = str(block["title"])
    lines = [_display_line(line) for line in block["lines"]]

    if key == "summary":
        return {
            "key": key,
            "title": title,
            "type": "summary",
            "paragraphs": _paragraphs_from_lines(lines),
        }
    if key == "education":
        return {
            "key": key,
            "title": title,
            "type": "education",
            "entries": _parse_education_entries(lines),
        }
    if key == "skills":
        return {
            "key": key,
            "title": title,
            "type": "skills",
            "groups": _parse_labeled_groups(lines),
        }
    if key == "projects":
        return {
            "key": key,
            "title": title,
            "type": "projects",
            "entries": _parse_project_entries(lines),
        }
    if key == "experience":
        return {
            "key": key,
            "title": title,
            "type": "experience",
            "entries": _parse_experience_entries(lines),
        }
    if key in {"achievements", "additional"}:
        return {
            "key": key,
            "title": title,
            "type": "categorized",
            "groups": _parse_labeled_groups(lines),
        }

    return {"key": key, "title": title, "type": "text", "paragraphs": _paragraphs_from_lines(lines)}


def _paragraphs_from_lines(lines: list[str]) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []

    for line in lines:
        clean = _display_line(line)
        if clean.startswith("\u2022"):
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
            paragraphs.append(clean.lstrip("\u2022 ").strip())
            continue

        current.append(clean)

    if current:
        paragraphs.append(" ".join(current).strip())

    return [paragraph for paragraph in paragraphs if paragraph]


def _parse_education_entries(lines: list[str]) -> list[dict[str, object]]:
    if not lines:
        return []

    content = " ".join(_display_line(line) for line in lines)
    date_range = _first_date_range(content)
    cgpa = _first_metric(content, r"CGPA[: ]+([0-9.]+(?:/[0-9.]+)?)")
    expected = _first_metric(content, r"Expected[: ]+([A-Za-z]{3,9}\s+\d{4})")
    degree = next((line for line in lines if "," in line or "b.tech" in line.lower() or "bachelor" in line.lower()), "")
    institution = next(
        (line for line in lines if any(word in line.lower() for word in ("university", "college", "school"))),
        "",
    )

    details = [line for line in (_display_line(line) for line in lines) if line not in {degree, institution}]
    return [
        {
            "title": degree or institution or "Education",
            "institution": institution,
            "dateRange": date_range,
            "cgpa": cgpa,
            "expected": expected,
            "details": details,
        }
    ]


def _parse_labeled_groups(lines: list[str]) -> list[dict[str, object]]:
    groups: list[dict[str, object]] = []

    for line in lines:
        clean = _display_line(line)
        if ":" not in clean:
            if groups:
                groups[-1]["notes"].append(clean)
            continue

        label, value = clean.split(":", maxsplit=1)
        items = _parse_tagged_items(value)
        groups.append(
            {
                "label": label.strip(),
                "items": items,
                "notes": [],
            }
        )

    return groups


def _parse_tagged_items(value: str) -> list[dict[str, str]]:
    cleaned = value.replace("\u2022", ", ")
    cleaned = re.sub(r"\bworking with\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace(";", ",")
    cleaned = re.sub(r"\s+and\s+", ", ", cleaned)
    parts = [part.strip() for part in cleaned.split(",") if part.strip()]
    items: list[dict[str, str]] = []

    for part in parts:
        status_match = STATUS_PATTERN.search(part)
        status = status_match.group(1).lower() if status_match else ""
        name = STATUS_PATTERN.sub("", part).strip(" -")
        if name:
            items.append({"name": name, "status": status})

    return items


def _parse_project_entries(lines: list[str]) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    current: dict[str, object] | None = None

    for line in lines:
        clean = _display_line(line)
        if not clean:
            continue

        if clean.startswith("\u2022"):
            if current:
                current["details"].append(clean.lstrip("\u2022 ").strip())
            continue

        if current and current["details"] and not _looks_like_project_heading(clean):
            current["details"][-1] = f"{current['details'][-1]} {clean}".strip()
            continue

        if _looks_like_project_heading(clean):
            title_part, stack_part = _split_once(clean, "|")
            name, subtitle = _split_heading_title(title_part)
            current = {
                "name": name,
                "subtitle": subtitle,
                "stack": [item.strip() for item in stack_part.split(",") if item.strip()] if stack_part else [],
                "details": [],
            }
            entries.append(current)
            continue

        if current:
            current["details"].append(clean)

    return entries


def _parse_experience_entries(lines: list[str]) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    current: dict[str, object] | None = None

    for line in lines:
        clean = _display_line(line)
        if not clean:
            continue

        if clean.startswith("\u2022"):
            if current:
                current["details"].append(clean.lstrip("\u2022 ").strip())
            continue

        if current and current["details"] and clean[:1].islower():
            current["details"][-1] = f"{current['details'][-1]} {clean}".strip()
            continue

        if _looks_like_experience_heading(clean):
            title, date_range = _split_date_from_heading(clean)
            current = {"title": title, "dateRange": date_range, "details": []}
            entries.append(current)
            continue

        if current:
            current["details"].append(clean)
        else:
            entries.append({"title": clean, "dateRange": "", "details": []})

    return entries


def _looks_like_project_heading(line: str) -> bool:
    if line.startswith("\u2022"):
        return False
    if len(line) > 110:
        return False
    return bool(re.search(r"(?:\s(?:-|\u2013|â€“)\s|\|)", line))


def _looks_like_experience_heading(line: str) -> bool:
    if line.startswith("\u2022"):
        return False
    if DATE_RANGE_PATTERN.search(line):
        return True
    if len(line.split()) <= 5 and ":" not in line:
        return True
    return False


def _split_heading_title(value: str) -> tuple[str, str]:
    for separator in (" \u2013 ", " - ", " \u2014 ", " â€“ ", " â€” "):
        if separator in value:
            left, right = value.split(separator, maxsplit=1)
            return left.strip(), right.strip()
    return value.strip(), ""


def _split_date_from_heading(value: str) -> tuple[str, str]:
    date_match = DATE_RANGE_PATTERN.search(value)
    if not date_match:
        return value.strip(), ""

    date_range = date_match.group()
    title = value.replace(date_range, "").strip(" |\u2013-")
    return title, date_range


def _split_once(value: str, separator: str) -> tuple[str, str]:
    if separator not in value:
        return value, ""
    left, right = value.split(separator, maxsplit=1)
    return left.strip(), right.strip()


def _extract_contact(header_lines: list[str], lines: list[str], text: str) -> dict[str, object]:
    email_match = EMAIL_PATTERN.search(text)
    phone_candidates = [match.group().strip() for match in PHONE_PATTERN.finditer(text)]
    phone = next((item for item in phone_candidates if sum(ch.isdigit() for ch in item) >= 10), None)

    links = {
        "linkedin": _extract_link(text, "linkedin"),
        "github": _extract_link(text, "github"),
        "leetcode": _extract_link(text, "leetcode"),
        "codechef": _extract_link(text, "codechef"),
        "portfolio": _portfolio_link(text),
    }

    name = _display_line(header_lines[0]) if header_lines else ""
    title = next(
        (
            _display_line(line)
            for line in header_lines
            if len(line) <= 80
            and any(role in line.lower() for role in ROLE_HINTS)
            and "seeking" not in line.lower()
        ),
        "",
    )
    location = next(
        (
            _display_line(line.split(":", maxsplit=1)[-1])
            for line in lines
            if line.lower().startswith(("location", "address"))
        ),
        "",
    )

    return {
        "name": name,
        "title": title,
        "email": email_match.group() if email_match else "",
        "phone": phone or "",
        "location": location,
        "links": {key: value for key, value in links.items() if value},
    }


def _extract_link(text: str, provider: str) -> str | None:
    provider_pattern = re.compile(rf"(https?://)?(?:www\.)?{provider}\.com/[^\s|]+", re.IGNORECASE)
    match = provider_pattern.search(text)
    if match:
        value = match.group().strip()
        return value if value.startswith("http") else f"https://{value}"
    return None


def _portfolio_link(text: str) -> str | None:
    direct_urls = [match.group() for match in URL_PATTERN.finditer(text)]
    for url in direct_urls:
        lowered = url.lower()
        if all(provider not in lowered for provider in ("linkedin.com", "github.com", "leetcode.com", "codechef.com")):
            return url

    for match in PLAIN_LINK_PATTERN.finditer(text):
        lowered = match.group().lower()
        if all(provider not in lowered for provider in ("linkedin.com", "github.com", "leetcode.com", "codechef.com")):
            return f"https://{match.group()}"
    return None


def _extract_skill_groups_from_sections(structured_sections: list[dict[str, object]]) -> list[dict[str, object]]:
    for section in structured_sections:
        if section.get("key") == "skills":
            return list(section.get("groups", []))
    return []


def _collect_learning_signals(structured_sections: list[dict[str, object]]) -> list[dict[str, str]]:
    signals: list[dict[str, str]] = []

    for section in structured_sections:
        if section.get("type") == "skills":
            for group in section.get("groups", []):
                for item in group.get("items", []):
                    if item.get("status"):
                        signals.append(
                            {
                                "section": section["title"],
                                "group": group["label"],
                                "name": item["name"],
                                "status": item["status"],
                            }
                        )

        if section.get("type") == "categorized":
            for group in section.get("groups", []):
                for item in group.get("items", []):
                    if item.get("status"):
                        signals.append(
                            {
                                "section": section["title"],
                                "group": group["label"],
                                "name": item["name"],
                                "status": item["status"],
                            }
                        )

    return signals


def _extract_skill_buckets(text: str) -> dict[str, list[str]]:
    lowered = text.lower()
    buckets: dict[str, list[str]] = {}

    for bucket, skills in SKILL_CATALOG.items():
        matched = []
        for skill in skills:
            pattern = re.escape(skill.lower()).replace(r"\ ", r"\s+")
            if re.search(rf"(?<!\w){pattern}(?!\w)", lowered):
                matched.append(skill)
        buckets[bucket] = matched

    return buckets


def _top_skills(skill_buckets: dict[str, list[str]], skill_groups: list[dict[str, object]]) -> list[str]:
    ordered: list[str] = []

    for group in skill_groups:
        for item in group.get("items", []):
            name = item["name"].lower()
            if name not in ordered:
                ordered.append(name)

    for bucket in ("languages", "frameworks", "data_ai", "cloud_devops", "tools", "soft_skills"):
        for skill in skill_buckets.get(bucket, []):
            lowered = skill.lower()
            if lowered not in ordered:
                ordered.append(lowered)

    return [skill.title() if skill.islower() and len(skill) > 3 else skill for skill in ordered]


def _extract_experience_timeline(structured_sections: list[dict[str, object]]) -> list[dict[str, str]]:
    timeline: list[dict[str, str]] = []

    for section in structured_sections:
        if section.get("key") not in {"experience", "education"}:
            continue

        for entry in section.get("entries", []):
            date_range = entry.get("dateRange", "")
            if not date_range:
                continue
            timeline.append(
                {
                    "dateRange": date_range,
                    "title": entry.get("title", ""),
                    "company": entry.get("institution", ""),
                    "context": " | ".join(entry.get("details", [])[:2]),
                }
            )

    return timeline[:12]


def _education_level(text: str) -> str:
    lowered = text.lower()
    if "ph.d" in lowered or "doctor of philosophy" in lowered:
        return "Doctorate"
    if "master of" in lowered or "m.tech" in lowered or "mba" in lowered or "msc" in lowered:
        return "Master's"
    if "bachelor" in lowered or "b.tech" in lowered or "b.e" in lowered or "bsc" in lowered:
        return "Bachelor's"
    if "diploma" in lowered:
        return "Diploma"
    return "Not clearly detected"


def _estimate_experience_years(text: str, timeline: list[dict[str, str]]) -> str:
    years = sorted(
        {
            int(match[-4:])
            for match in re.findall(r"\b(?:19\d{2}|20\d{2}|(?:0[1-9]|1[0-2])/\d{4})\b", text)
            if match[-4:].isdigit()
        }
    )
    if len(years) >= 2:
        span = max(years) - min(years)
        if span > 0:
            return f"{span}+ years"

    if timeline:
        return f"{len(timeline)} dated entries"

    return "Insufficient data"


def _find_structured_entries(structured_sections: list[dict[str, object]], section_key: str) -> list[dict[str, object]]:
    for section in structured_sections:
        if section.get("key") == section_key:
            return list(section.get("entries", []))
    return []


def _build_insights(
    profile: dict[str, object],
    top_skills: list[str],
    structured_sections: list[dict[str, object]],
    learning_signals: list[dict[str, str]],
) -> list[str]:
    insights: list[str] = []

    if profile.get("email") and profile.get("phone"):
        insights.append("Contact details include both email and phone number.")
    elif profile.get("email"):
        insights.append("Email address detected, but phone number was not confidently identified.")
    else:
        insights.append("Primary contact details are incomplete and may need manual review.")

    project_entries = _find_structured_entries(structured_sections, "projects")
    if project_entries:
        insights.append(f"Detected {len(project_entries)} named project entries with structured descriptions.")

    if top_skills:
        insights.append(f"Top skill signals: {', '.join(top_skills[:5])}.")

    if learning_signals:
        learning_preview = ", ".join(signal["name"] for signal in learning_signals[:4])
        insights.append(f"Learning and in-progress signals captured for: {learning_preview}.")

    return insights


def _first_date_range(text: str) -> str:
    match = DATE_RANGE_PATTERN.search(text)
    return match.group() if match else ""


def _first_metric(text: str, pattern: str) -> str:
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else ""
