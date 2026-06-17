import pytest

from git_tutorial.models import QuizQuestion
from git_tutorial.content import get_quiz_questions
from git_tutorial.quiz import QuizEngine


class TestQuizEngine:
    def test_load_questions(self):
        engine = QuizEngine()
        questions = engine.load_questions()
        assert len(questions) > 0
        for q in questions:
            assert isinstance(q, QuizQuestion)

    def test_load_questions_all_have_answer(self):
        engine = QuizEngine()
        questions = engine.load_questions()
        for q in questions:
            assert q.answer, f"Question missing answer: {q.question[:50]}"

    def test_mcq_validation(self):
        q = QuizQuestion(
            question="Test?",
            answer="Option A",
            options=["Option A", "Option B", "Option C"],
            answer_index=0,
        )
        assert q.is_mcq

    def non_mcq(self):
        q = QuizQuestion(question="Open ended?", answer="Some answer")
        assert not q.is_mcq


class TestQuizQuestionsInContent:
    def test_phase_1_has_questions(self, phases):
        for t in phases[0].topics:
            qs = get_quiz_questions(t)
            if qs:
                return
        pytest.fail("Phase 1 has no quiz questions")

    def test_question_structure(self, phases):
        for p in phases:
            for t in p.topics:
                for q in get_quiz_questions(t):
                    assert q.question
                    assert len(q.question) > 5
                    assert q.answer
                    assert len(q.options) >= 2
                    assert q.answer_index >= 0
                    assert 0 <= q.answer_index < len(q.options)
                    assert q.options[q.answer_index] == q.answer
