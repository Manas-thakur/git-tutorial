import subprocess
import tempfile
import shlex
import re
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


GIT_COMMANDS = [
    "add", "am", "archive", "bisect", "blame", "branch", "bundle", "checkout",
    "cherry-pick", "citool", "clean", "clone", "commit", "config", "describe",
    "diff", "fetch", "format-patch", "fsck", "gc", "grep", "help", "init",
    "log", "maintenance", "merge", "mergetool", "mktag", "mktree", "mv",
    "notes", "prune", "pull", "push", "rebase", "reflog", "remote", "reset",
    "restore", "revert", "rm", "shortlog", "show", "show-ref", "sparse-checkout",
    "stash", "status", "submodule", "switch", "tag", "update-index",
    "update-ref", "verify-commit", "verify-tag", "whatchanged", "worktree",
]


ALLOWED_OPS = {"echo", "printf", "cat", "mkdir", "touch", "ls", "pwd", "head", "tail", "wc", "sort", "grep"}

BLOCKED_RE = re.compile(r"[;&|`$!{}()]")

DANGEROUS_PATHS = {"/", "/etc", "/usr", "/dev", "/proc", "/sys", "/bin", "/sbin", "/lib", "/boot", "/root", "/home"}


def _is_safe_path(command: str, parts: list[str], repo_path: Path) -> bool:
    for p in parts[1:]:
        p = p.strip("\"'")
        if p in DANGEROUS_PATHS:
            return False
        if p.startswith("/"):
            return False
        if ".." in p.split("/"):
            return False
    return True


def _parse_echo_redirect(command: str, repo_path: Path) -> Optional[tuple]:
    rest = command[len("echo"):].strip() if command.lower().startswith("echo") else command[len("printf"):].strip()
    m = re.match(r'''["']?(.+?)["']?\s*(>>?)\s*(.+)$''', rest)
    if not m:
        return None
    text = m.group(1).strip().strip("\"'")
    op = m.group(2)
    target = m.group(3).strip().strip("\"'")
    if target in DANGEROUS_PATHS or target.startswith("/") or ".." in target.split("/"):
        return None
    target_path = repo_path / target
    try:
        target_path = target_path.resolve()
        if not str(target_path).startswith(str(repo_path.resolve())):
            return None
    except (OSError, ValueError):
        pass
    return (text, op, target_path)


def validate_command(command: str) -> tuple[bool, str]:
    if not command.strip():
        return False, "Empty command"
    if BLOCKED_RE.search(command):
        return False, "Command contains blocked characters (;, |, &, $, !, {, }, (, ), `)"
    try:
        parts = shlex.split(command)
    except ValueError as e:
        return False, f"Malformed command: {e}"
    if not parts:
        return False, "Empty command"
    cmd = parts[0].lower()
    if cmd == "git":
        return True, ""
    if cmd in ALLOWED_OPS:
        for p in parts[1:]:
            if ".." in p:
                return False, "Path traversal not allowed"
        return True, ""
    return False, f"Command not allowed: {cmd}. Use a git command or one of: {', '.join(sorted(ALLOWED_OPS))}"


def _run_git(args: list[str], cwd: Path, timeout: int = 10) -> dict:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Command timed out (10s)", "success": False, "returncode": -1}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "success": False, "returncode": -1}


class GitSandbox:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="gittut_")
        self.repo_path = Path(self.temp_dir)
        self.remote_path: Optional[Path] = None
        self._init_repo()

    def _init_repo(self):
        subprocess.run(["git", "init"], cwd=self.repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Git Tutorial User"], cwd=self.repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "user@example.com"], cwd=self.repo_path, capture_output=True)
        subprocess.run(["git", "branch", "-m", "main"], cwd=self.repo_path, capture_output=True)

    def setup_remote(self) -> None:
        remote_temp = tempfile.mkdtemp(prefix="gittut_remote_")
        self.remote_path = Path(remote_temp)
        subprocess.run(["git", "init", "--bare"], cwd=self.remote_path, capture_output=True)
        subprocess.run(["git", "symbolic-ref", "HEAD", "refs/heads/main"], cwd=self.remote_path, capture_output=True)
        _run_git(["remote", "add", "origin", str(self.remote_path)], self.repo_path)
        _run_git(["config", "remote.origin.push", "main"], self.repo_path)

    def reset_repo(self) -> None:
        import shutil
        for d in [self.temp_dir, str(self.remote_path)] if self.remote_path else [self.temp_dir]:
            shutil.rmtree(d, ignore_errors=True)
        self.temp_dir = tempfile.mkdtemp(prefix="gittut_")
        self.repo_path = Path(self.temp_dir)
        self.remote_path = None
        self._init_repo()

    def run_command(self, command: str) -> dict:
        valid, msg = validate_command(command)
        if not valid:
            return {"stdout": "", "stderr": msg, "success": False, "returncode": -1}

        parts = shlex.split(command)
        cmd = parts[0].lower()

        if cmd == "git":
            return _run_git(parts[1:], self.repo_path)

        if cmd in ("echo", "printf"):
            return self._run_shell_echo(command, parts)

        if ">" in parts or ">>" in parts:
            return {"stdout": "", "stderr": "Redirection is only supported with echo/printf. Use 'echo text > filename' to write files.", "success": False, "returncode": -1}
        if "<" in parts:
            return {"stdout": "", "stderr": "Input redirection is not supported in the sandbox.", "success": False, "returncode": -1}

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": "Command timed out (10s)", "success": False, "returncode": -1}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "success": False, "returncode": -1}

    def _run_shell_echo(self, command: str, parts: list[str]) -> dict:
        cmd = parts[0].lower()
        has_redirect = ">" in parts or ">>" in parts
        parsed = _parse_echo_redirect(command, self.repo_path)
        if parsed is not None:
            text, op, target_path = parsed
            try:
                if op == ">":
                    target_path.write_text(text + "\n")
                else:
                    with target_path.open("a") as f:
                        f.write(text + "\n")
                return {"stdout": "", "stderr": "", "success": True, "returncode": 0}
            except Exception as e:
                return {"stdout": "", "stderr": str(e), "success": False, "returncode": -1}
        if has_redirect:
            return {"stdout": "", "stderr": "Invalid redirect target: path must be inside the repository", "success": False, "returncode": -1}
        rest = command[len(cmd):].strip().strip("\"'")
        return {"stdout": rest + "\n", "stderr": "", "success": True, "returncode": 0}

    def create_initial_commit(self):
        readme = self.repo_path / "README.md"
        readme.write_text("# Git Tutorial Sandbox\n\nPractice your git commands here.\n")
        self.run_command("git add README.md")
        self.run_command('git commit -m "Initial commit"')

    def _safe_run(self, cmd_list: list[str]) -> dict:
        try:
            result = subprocess.run(cmd_list, cwd=self.repo_path, capture_output=True, text=True, timeout=10)
            return {"stdout": result.stdout, "stderr": result.stderr, "success": result.returncode == 0, "returncode": result.returncode}
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": "Timed out", "success": False, "returncode": -1}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "success": False, "returncode": -1}

    def get_graph(self) -> str:
        r = self._safe_run(["git", "log", "--all", "--oneline", "--graph", "--decorate"])
        if r["success"] and r["stdout"]:
            lines = []
            for line in r["stdout"].splitlines():
                colored = line.replace("*", "[bold yellow]*[/]")
                colored = colored.replace("|", "[dim]|[/]")
                colored = colored.replace("/", "[dim]/[/]")
                colored = colored.replace("\\", "[dim]\\[/]")
                lines.append(colored)
            return "\n".join(lines)
        return "[dim](no commits yet)[/]"

    def get_status(self) -> str:
        r = self._safe_run(["git", "status", "--short", "--branch"])
        if r["success"] and r["stdout"]:
            lines = []
            for line in r["stdout"].splitlines():
                s = line.strip()
                if s.startswith("##"):
                    lines.append(f"[cyan]{s}[/]")
                elif s.startswith("M") or s.startswith("A") or s.startswith("D"):
                    lines.append(f"[green]{s}[/]")
                elif s.startswith("?"):
                    lines.append(f"[red]{s}[/]")
                else:
                    lines.append(s)
            return "\n".join(lines)
        return "[dim](clean working tree)[/]"

    def get_diff(self) -> str:
        r = self._safe_run(["git", "diff"])
        if not r["success"] or not r["stdout"]:
            r2 = self._safe_run(["git", "diff", "--staged"])
            if r2["success"] and r2["stdout"]:
                return self._highlight_diff(r2["stdout"])
            return "[dim](no changes to diff)[/]"
        return self._highlight_diff(r["stdout"])

    def _highlight_diff(self, diff_text: str) -> str:
        lines = []
        for line in diff_text.splitlines():
            if line.startswith("+++") or line.startswith("---"):
                lines.append(f"[bold cyan]{line}[/]")
            elif line.startswith("@@"):
                lines.append(f"[bold magenta]{line}[/]")
            elif line.startswith("+"):
                lines.append(f"[green]{line}[/]")
            elif line.startswith("-"):
                lines.append(f"[red]{line}[/]")
            elif line.startswith("diff ") or line.startswith("index "):
                lines.append(f"[dim]{line}[/]")
            else:
                lines.append(line)
        return "\n".join(lines)

    def get_branches(self) -> list[str]:
        r = self._safe_run(["git", "branch"])
        if r["success"] and r["stdout"]:
            branches = [b.strip().lstrip("* ") for b in r["stdout"].splitlines() if b.strip()]
            if branches:
                return branches
        r2 = self._safe_run(["git", "symbolic-ref", "--short", "HEAD"])
        if r2["success"] and r2["stdout"].strip():
            return [r2["stdout"].strip()]
        return []

    def cleanup(self):
        import shutil
        paths = [self.temp_dir]
        if self.remote_path:
            paths.append(str(self.remote_path))
        for p in paths:
            shutil.rmtree(p, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cleanup()


def sandbox_loop(sandbox: GitSandbox = None):
    if sandbox is None:
        sandbox = GitSandbox()
    from rich.panel import Panel
    console.print(Panel(
        "[bold yellow]Git Sandbox[/]\n\n"
        "Type git commands and see results instantly.\n"
        "Type [bold]exit[/] or [bold]quit[/] to return.\n"
        "Type [bold]init[/] to create an initial commit with a README.",
        border_style="yellow",
        title="Git Playground",
    ))
    try:
        while True:
            cmd = input("  $ ")
            if cmd.strip().lower() in ("exit", "quit"):
                break
            if cmd.strip().lower() == "init":
                sandbox.create_initial_commit()
                console.print("[green]Initial commit created.[/]")
                continue
            if not cmd.strip():
                continue
            result = sandbox.run_command(cmd)
            if result["stdout"]:
                console.print(result["stdout"].rstrip())
            if result["stderr"]:
                console.print(f"[red]{result['stderr'].rstrip()}[/]")
            if not result["success"] and not result["stderr"]:
                console.print(f"[red]Command failed with code {result['returncode']}[/]")
    except (EOFError, KeyboardInterrupt):
        console.print("\n[dim]Exiting sandbox.[/]")
