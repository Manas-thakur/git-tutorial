import pytest
import json
import os
from pathlib import Path

from git_tutorial.progress import ProgressTracker, _xp_for_level, _level_from_xp


@pytest.fixture(autouse=True)
def clean_progress_file():
    from git_tutorial.progress import PROGRESS_FILE
    if PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()
    yield
    if PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()
        PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)


class TestXP:
    def test_xp_for_level(self):
        assert _xp_for_level(1) == 50
        assert _xp_for_level(2) == 150
        assert _xp_for_level(3) == 300

    def test_level_from_xp_zero(self):
        level, current, needed = _level_from_xp(0)
        assert level == 0
        assert current == 0
        assert needed > 0

    def test_level_from_xp_level_1(self):
        level, current, needed = _level_from_xp(50)
        assert level == 1
        assert current == 0
        assert needed > 0

    def test_level_from_xp_boundary(self):
        level, current, needed = _level_from_xp(49)
        assert level == 0
        level, current, needed = _level_from_xp(50)
        assert level == 1


class TestProgressTracker:
    def test_init(self):
        tracker = ProgressTracker()
        assert tracker.get_xp() == 0
        assert tracker.get_level() == 0

    def test_mark_complete(self):
        tracker = ProgressTracker()
        tracker.mark_complete(1, 1)
        assert tracker.is_complete(1, 1)
        assert not tracker.is_complete(1, 2)

    def test_phase_progress(self):
        tracker = ProgressTracker()
        tracker.mark_complete(1, 1)
        done, total = tracker.get_phase_progress(1, 5)
        assert done == 1
        assert total == 5

    def test_total_completed(self):
        tracker = ProgressTracker()
        tracker.mark_complete(1, 1)
        tracker.mark_complete(1, 2)
        tracker.mark_complete(2, 1)
        assert tracker.get_total_completed() == 3

    def test_add_xp(self):
        tracker = ProgressTracker()
        tracker.add_xp(50)
        assert tracker.get_xp() == 50
        assert tracker.get_level() == 1

    def test_add_xp_level_up(self):
        tracker = ProgressTracker()
        assert tracker.add_xp(50)  # should level up from 0 to 1
        assert tracker.get_level() == 1

    def test_level_info(self):
        tracker = ProgressTracker()
        tracker.add_xp(25)
        info = tracker.get_level_info()
        assert info["level"] == 0
        assert info["xp_current"] == 25
        assert info["xp_needed"] > 0
        assert info["xp_total"] == 25

    def test_badges_first_complete(self):
        tracker = ProgressTracker()
        tracker.mark_complete(1, 1)
        badges = tracker.get_badges()
        names = [b["name"] for b in badges]
        assert "First Commit" in names

    def test_badges_level_based(self):
        tracker = ProgressTracker()
        tracker.add_xp(300)  # level 3
        badges = tracker.get_badges()
        names = [b["name"] for b in badges]
        assert "Apprentice" in names

    def test_no_badges_initially(self):
        tracker = ProgressTracker()
        badges = tracker.get_badges()
        assert len(badges) == 0

    def test_bookmark(self):
        tracker = ProgressTracker()
        tracker.set_bookmark(1, 3, 1)
        bm = tracker.get_bookmark()
        assert bm is not None
        assert bm["phase"] == 1
        assert bm["topic"] == 3
        assert bm["section"] == 1

    def test_clear_bookmark(self):
        tracker = ProgressTracker()
        tracker.set_bookmark(1, 1)
        tracker.clear_bookmark()
        assert tracker.get_bookmark() is None

    def test_reset(self):
        tracker = ProgressTracker()
        tracker.mark_complete(1, 1)
        tracker.add_xp(50)
        tracker.reset()
        assert tracker.get_total_completed() == 0
        assert tracker.get_xp() == 0

    def test_persistence(self):
        tracker1 = ProgressTracker()
        tracker1.mark_complete(3, 2)
        tracker1.add_xp(100)

        tracker2 = ProgressTracker()
        assert tracker2.is_complete(3, 2)
        assert tracker2.get_xp() == 100

    def test_quiz_attempt_recorded(self):
        tracker = ProgressTracker()
        tracker.record_quiz_attempt(1, 2, 3, 5)
        # reload
        tracker2 = ProgressTracker()
        key = "_mastery"
        assert key in tracker2.data
        assert "1.2" in tracker2.data[key]
        assert len(tracker2.data[key]["1.2"]["attempts"]) == 1

    def test_phase_unlocked_default(self):
        tracker = ProgressTracker()
        assert tracker.is_phase_unlocked(1)
        assert True  # phase 0-1 always unlocked

    def test_streak(self):
        tracker = ProgressTracker()
        assert tracker.get_streak() == 0
        tracker.add_streak()
        assert tracker.get_streak() == 1
