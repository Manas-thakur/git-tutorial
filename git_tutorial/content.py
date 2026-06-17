import re
from pathlib import Path
from typing import Optional

from .models import Phase, Topic, Section, QuizQuestion

CONTENT_DIR = Path(__file__).parent / "content"


def _parse_sections(text: str) -> list[Section]:
    sections: list[Section] = []
    lines = text.splitlines()
    current_heading: Optional[str] = None
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current_heading is not None:
                sections.append(
                    Section(
                        heading=current_heading,
                        content="\n".join(current_lines).strip(),
                    )
                )
            current_heading = line.removeprefix("## ").strip()
            current_lines = []
        elif current_heading is not None:
            current_lines.append(line)

    if current_heading is not None:
        sections.append(
            Section(
                heading=current_heading,
                content="\n".join(current_lines).strip(),
            )
        )

    return sections


def _parse_quiz_questions(content: str) -> list[QuizQuestion]:
    lines = content.splitlines()

    answer_map = {}
    for line in lines:
        stripped = line.strip()
        m = re.match(r"\*\*Answers?\*\*:?\s*(.+)", stripped, re.IGNORECASE)
        if m:
            for part in m.group(1).split(","):
                part = part.strip()
                m2 = re.match(r"(\d+)\s*[-.)]\s*([a-e])", part)
                if m2:
                    answer_map[int(m2.group(1))] = ord(m2.group(2)) - ord("a")
            break

    questions = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        m = re.match(r"\*\*(?:Q|Question)\s*(\d+)[\.:\)]?\*\*\s*(.*)", stripped)
        if not m:
            continue
        q_num = int(m.group(1))
        q_text = m.group(2).strip()
        options = []
        j = i + 1
        while j < len(lines):
            opt_line = lines[j].strip()
            if not opt_line:
                j += 1
                continue
            om = re.match(r"^([a-e])\)\s*(.+)", opt_line)
            if om:
                options.append(om.group(2).strip())
                j += 1
            elif opt_line.startswith("**") and "**" in opt_line[2:]:
                break
            else:
                j += 1
        if options:
            ans_idx = answer_map.get(q_num, -1)
            answer = options[ans_idx] if 0 <= ans_idx < len(options) else (options[0] if options else "")
            questions.append(QuizQuestion(
                question=q_text,
                answer=answer,
                options=list(options),
                answer_index=ans_idx if 0 <= ans_idx < len(options) else -1,
            ))

    return questions


def discover_phases(content_dir: Optional[Path] = None) -> list[Phase]:
    base = content_dir or CONTENT_DIR
    if not base.exists():
        return []
    phases: list[Phase] = []
    for d in sorted(base.iterdir()):
        if not d.is_dir():
            continue
        match = re.match(r"(\d+)[- ](.+)", d.name)
        if match:
            num = int(match.group(1))
            title = match.group(2).replace("-", " ").strip()
        else:
            num = 0
            title = d.name
        phase = Phase(number=num, title=title, path=d)
        md_files = sorted(d.glob("*.md"))
        for i, f in enumerate(md_files, start=1):
            name_parts = f.stem.split(". ", 1)
            topic_title = name_parts[1] if len(name_parts) > 1 else f.stem
            topic = Topic(number=i, title=topic_title, filepath=f)
            text = f.read_text(encoding="utf-8")
            topic.sections = _parse_sections(text)
            phase.topics.append(topic)
        phases.append(phase)
    return phases


def get_phase(number: int, content_dir: Optional[Path] = None) -> Optional[Phase]:
    for p in discover_phases(content_dir):
        if p.number == number:
            return p
    return None


def get_topic(phase_number: int, topic_number: int, content_dir: Optional[Path] = None) -> Optional[Topic]:
    phase = get_phase(phase_number, content_dir)
    if not phase:
        return None
    if topic_number < 1 or topic_number > len(phase.topics):
        return None
    return phase.topics[topic_number - 1]


def get_quiz_questions(topic: Topic) -> list[QuizQuestion]:
    for s in topic.sections:
        questions = _parse_quiz_questions(s.content)
        if questions:
            return questions
    return []


def search_content(query: str, phases: list[Phase]) -> list[dict]:
    results: list[dict] = []
    q = query.lower()
    for p in phases:
        for t in p.topics:
            text = t.filepath.read_text(encoding="utf-8")
            lines = text.splitlines()
            matches = [(i + 1, line.strip()) for i, line in enumerate(lines) if q in line.lower()]
            if matches:
                results.append({
                    "phase": p.number,
                    "topic": t.number,
                    "title": t.title,
                    "matches": matches[:20],
                })
    return results
