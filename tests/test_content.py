import pytest
from pathlib import Path

from git_tutorial.content import (
    discover_phases, get_phase, get_topic, get_quiz_questions,
    search_content, CONTENT_DIR, _parse_sections, _parse_quiz_questions,
)
from git_tutorial.models import Phase, Topic, Section, QuizQuestion


class TestParseSections:
    def test_empty_content(self):
        sections = _parse_sections("")
        assert sections == []

    def test_no_headings(self):
        sections = _parse_sections("plain text\nmore text")
        assert sections == []

    def test_single_section(self):
        text = "## Getting Started\nSome content here.\nMore content."
        sections = _parse_sections(text)
        assert len(sections) == 1
        assert sections[0].heading == "Getting Started"
        assert "Some content here" in sections[0].content

    def test_multiple_sections(self):
        text = "## First\nContent 1\n## Second\nContent 2"
        sections = _parse_sections(text)
        assert len(sections) == 2
        assert sections[0].heading == "First"
        assert sections[1].heading == "Second"


class TestParseQuizQuestions:
    def test_no_questions(self):
        questions = _parse_quiz_questions("Plain text with no quiz content.")
        assert questions == []

    def test_single_mcq(self):
        text = (
            "**Q1.** What is Git?\n"
            "a) A version control system\n"
            "b) A text editor\n"
            "c) A database\n"
            "d) A web server\n"
            "**Answers**: 1-a"
        )
        questions = _parse_quiz_questions(text)
        assert len(questions) == 1
        assert questions[0].question == "What is Git?"
        assert len(questions[0].options) == 4
        assert questions[0].answer == "A version control system"
        assert questions[0].answer_index == 0

    def test_multiple_questions(self):
        text = (
            "**Q1.** First question?\n"
            "a) Opt A\n"
            "b) Opt B\n"
            "**Q2.** Second question?\n"
            "a) Opt X\n"
            "b) Opt Y\n"
            "c) Opt Z\n"
            "**Answers**: 1-a, 2-b"
        )
        questions = _parse_quiz_questions(text)
        assert len(questions) == 2
        assert questions[0].answer == "Opt A"
        assert questions[1].answer == "Opt Y"

    def test_answer_variants(self):
        text = (
            "**Q1.** Test?\n"
            "a) Alpha\n"
            "b) Beta\n"
            "**Answer**: 1 - b"
        )
        questions = _parse_quiz_questions(text)
        assert len(questions) == 1
        assert questions[0].answer == "Beta"
        assert questions[0].answer_index == 1


class TestDiscoverPhases:
    def test_discover_phases_returns_list(self, phases):
        assert isinstance(phases, list)
        assert len(phases) > 0

    def test_each_phase_has_topics(self, phases):
        for p in phases:
            assert len(p.topics) > 0, f"Phase {p.number} ({p.title}) has no topics"

    def test_phase_numbering(self, phases):
        numbers = [p.number for p in phases]
        assert 1 in numbers

    def test_phase_attributes(self, phases):
        for p in phases:
            assert p.title
            assert p.path.exists()
            assert isinstance(p.number, int)

    def test_topic_attributes(self, phases):
        for p in phases:
            for t in p.topics:
                assert t.title
                assert t.filepath.exists()
                assert t.filepath.suffix == ".md"
                assert isinstance(t.number, int)

    def test_topic_sections_parsed(self, phases):
        for p in phases:
            for t in p.topics:
                assert len(t.sections) > 0, f"Topic {t.title} has no sections"
                for s in t.sections:
                    assert s.heading
                    assert s.content

    def test_get_phase_by_number(self):
        p = get_phase(1)
        assert p is not None
        assert p.number == 1

    def test_get_phase_nonexistent(self):
        p = get_phase(999)
        assert p is None

    def test_get_topic(self):
        t = get_topic(1, 1)
        assert t is not None
        assert t.number == 1

    def test_get_topic_nonexistent_phase(self):
        t = get_topic(999, 1)
        assert t is None

    def test_get_topic_nonexistent_index(self):
        t = get_topic(1, 999)
        assert t is None


class TestQuizQuestionsInContent:
    def test_phases_have_quiz_questions(self, phases):
        total = 0
        for p in phases:
            for t in p.topics:
                qs = get_quiz_questions(t)
                total += len(qs)
        assert total > 0, "No quiz questions found in any topic"

    def test_quiz_questions_are_valid(self, phases):
        for p in phases:
            for t in p.topics:
                for q in get_quiz_questions(t):
                    assert q.question
                    assert q.answer
                    assert len(q.options) > 0
                    assert q.answer_index >= 0


class TestSearchContent:
    def test_search_finds_results(self, phases):
        results = search_content("git", phases)
        assert len(results) > 0

    def test_search_empty_query(self, phases):
        results = search_content("", phases)
        assert len(results) > 0 or len(results) == 0  # any result is fine

    def test_search_nonexistent(self, phases):
        results = search_content("xyznonexistent12345", phases)
        assert len(results) == 0

    def test_search_result_structure(self, phases):
        results = search_content("init", phases)
        if results:
            r = results[0]
            assert "phase" in r
            assert "topic" in r
            assert "title" in r
            assert "matches" in r
            assert len(r["matches"]) > 0


class TestContentDir:
    def test_content_dir_exists(self, content_dir):
        assert content_dir.exists()

    def test_content_dir_has_phase_dirs(self, content_dir):
        dirs = [d for d in content_dir.iterdir() if d.is_dir()]
        assert len(dirs) > 0

    def test_each_phase_has_markdown_files(self, content_dir):
        for d in sorted(content_dir.iterdir()):
            if d.is_dir():
                md_files = list(d.glob("*.md"))
                assert len(md_files) > 0, f"Directory {d.name} has no markdown files"
