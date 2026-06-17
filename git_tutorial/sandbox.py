import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.syntax import Syntax


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


class GitSandbox:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="gittut_")
        self.repo_path = Path(self.temp_dir)
        self._init_repo()

    def _init_repo(self, keep_config: bool = False):
        subprocess.run(["git", "init"], cwd=self.repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Git Tutorial User"], cwd=self.repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "user@example.com"], cwd=self.repo_path, capture_output=True)
        subprocess.run(["git", "config", "init.defaultBranch", "main"], cwd=self.repo_path, capture_output=True)

    def reset_repo(self) -> None:
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir = tempfile.mkdtemp(prefix="gittut_")
        self.repo_path = Path(self.temp_dir)
        self._init_repo()

    def run_command(self, command: str) -> dict:
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

    def create_initial_commit(self):
        readme = self.repo_path / "README.md"
        readme.write_text("# Git Tutorial Sandbox\n\nPractice your git commands here.\n")
        self.run_command("git add README.md")
        self.run_command('git commit -m "Initial commit"')

    def get_graph(self) -> str:
        r = self.run_command("git log --all --oneline --graph --decorate 2>/dev/null | head -40")
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
        r = self.run_command("git status --short --branch 2>/dev/null")
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
        r = self.run_command("git diff 2>/dev/null")
        if not r["success"] or not r["stdout"]:
            r2 = self.run_command("git diff --staged 2>/dev/null")
            if r2["success"] and r2["stdout"]:
                return self._highlight_diff(r2["stdout"], staged=True)
            return "[dim](no changes to diff)[/]"
        return self._highlight_diff(r["stdout"])

    def _highlight_diff(self, diff_text: str, staged: bool = False) -> str:
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
        r = self.run_command("git branch")
        if r["success"] and r["stdout"]:
            return [b.strip().lstrip("* ") for b in r["stdout"].splitlines() if b.strip()]
        return []

    def cleanup(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cleanup()


def sandbox_loop(sandbox: GitSandbox = None):
    if sandbox is None:
        sandbox = GitSandbox()

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
