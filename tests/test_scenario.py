import pytest

from git_tutorial.scenario import (
    Scenario, Step, get_scenario, setup_scenario, validate_step,
    verify_scenario_complete, SCENARIOS,
)
from git_tutorial.sandbox import GitSandbox


class TestScenarioData:
    def test_scenarios_defined(self):
        assert len(SCENARIOS) > 0

    def test_each_scenario_has_required_fields(self):
        for key, s in SCENARIOS.items():
            assert isinstance(s, Scenario)
            assert s.phase >= 1
            assert s.topic >= 1
            assert s.title
            assert s.goal
            assert len(s.steps) > 0

    def test_each_step_has_required_fields(self):
        for key, s in SCENARIOS.items():
            for i, step in enumerate(s.steps):
                assert step.expected_pattern, f"Step {i} in {key} missing pattern"
                assert step.description, f"Step {i} in {key} missing description"
                assert step.hint, f"Step {i} in {key} missing hint"

    def test_scenario_keys_match_phase_topic(self):
        for key, s in SCENARIOS.items():
            assert key == f"{s.phase}.{s.topic}"

    def test_known_scenarios_exist(self):
        assert "1.2" in SCENARIOS
        assert "1.4" in SCENARIOS
        assert "1.5" in SCENARIOS
        assert "2.2" in SCENARIOS
        assert "2.3" in SCENARIOS


class TestGetScenario:
    def test_get_existing(self):
        s = get_scenario(1, 2)
        assert s is not None
        assert s.title == "Your First Repo"

    def test_get_nonexistent(self):
        s = get_scenario(99, 99)
        assert s is None

    def test_get_topic_5_scenario(self):
        s = get_scenario(1, 5)
        assert s is not None
        assert "History" in s.title


class TestValidateStep:
    @pytest.fixture
    def scenario(self):
        return get_scenario(1, 2)

    def test_correct_step_match(self, scenario):
        ok, msg = validate_step("git init", scenario, 0)
        assert ok
        assert "complete" in msg

    def test_wrong_step(self, scenario):
        ok, msg = validate_step("git status", scenario, 0)
        assert not ok
        assert "Hint" in msg

    def test_step_out_of_range(self, scenario):
        ok, msg = validate_step("anything", scenario, 99)
        assert not ok
        assert "All steps complete" in msg


class TestSetupScenario:
    def test_setup_creates_initial_state(self, sandbox):
        scenario = get_scenario(1, 4)
        setup_scenario(sandbox, scenario)
        r = sandbox.run_command("git log --oneline")
        assert r["success"]
        assert "Initial commit" in r["stdout"]

    def test_setup_no_commands(self, sandbox):
        scenario = get_scenario(1, 2)
        setup_scenario(sandbox, scenario)
        r = sandbox.run_command("git log --oneline")
        assert not r["success"] or "Initial" not in r["stdout"]


class TestVerifyComplete:
    def test_all_steps_complete(self):
        s = get_scenario(1, 2)
        result = verify_scenario_complete(None, s, list(range(len(s.steps))))
        assert "complete" in result

    def test_some_steps_remaining(self):
        s = get_scenario(1, 2)
        result = verify_scenario_complete(None, s, [0, 1])
        assert "remaining" in result


class TestScenarioExecution:
    def test_scenario_1_2_full_flow(self, sandbox):
        scenario = get_scenario(1, 2)
        setup_scenario(sandbox, scenario)
        commands = [
            "git init",
            "echo '# My Project' > README.md",
            "git add README.md",
            "git commit -m 'First commit'",
            "git log --oneline",
        ]
        for i, cmd in enumerate(commands):
            ok, msg = validate_step(cmd, scenario, i)
            assert ok, f"Step {i} failed: {msg}"
        result = verify_scenario_complete(sandbox, scenario, list(range(len(commands))))
        assert "complete" in result

    def test_scenario_1_4_full_flow(self, sandbox):
        scenario = get_scenario(1, 4)
        setup_scenario(sandbox, scenario)
        commands = [
            "echo 'line 2' >> file.txt",
            "git status",
            "git diff",
            "git add file.txt",
            "git diff --staged",
            "git commit -m 'Add line 2'",
        ]
        for i, cmd in enumerate(commands):
            ok, msg = validate_step(cmd, scenario, i)
            assert ok, f"Step {i} failed: {msg}"

    def test_scenario_1_5_full_flow(self, sandbox):
        scenario = get_scenario(1, 5)
        setup_scenario(sandbox, scenario)
        commands = [
            "echo 'alpha' > file1.txt",
            "git add file1.txt",
            "git commit -m 'First file'",
            "echo 'beta' > file2.txt",
            "git add file2.txt",
            "git commit -m 'Second file'",
            "echo 'gamma' > file3.txt",
            "git add file3.txt",
            "git commit -m 'Third file'",
            "git log --oneline",
            "git log --oneline --graph",
        ]
        for i, cmd in enumerate(commands):
            ok, msg = validate_step(cmd, scenario, i)
            assert ok, f"Step {i} failed: {msg}"

    def test_scenario_2_2_full_flow(self, sandbox):
        scenario = get_scenario(2, 2)
        setup_scenario(sandbox, scenario)
        commands = [
            "git branch",
            "git branch feature",
            "git branch",
            "git switch feature",
            "echo 'feature work' > feature.txt",
            "git add feature.txt",
            "git commit -m 'Feature work'",
            "git switch main",
            "git log --oneline --all --graph",
        ]
        for i, cmd in enumerate(commands):
            ok, msg = validate_step(cmd, scenario, i)
            assert ok, f"Step {i} failed: {msg}"

    def test_scenario_2_3_full_flow(self, sandbox):
        scenario = get_scenario(2, 3)
        setup_scenario(sandbox, scenario)
        commands = [
            "git branch",
            "git log --oneline --all --graph",
            "git merge feature",
            "git log --oneline --graph",
        ]
        for i, cmd in enumerate(commands):
            ok, msg = validate_step(cmd, scenario, i)
            assert ok, f"Step {i} failed: {msg}"
