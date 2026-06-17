import subprocess
import tempfile
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


console = Console()


class GitSandbox:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="gittut_")
        self.repo_path = Path(self.temp_dir)
        self._init_repo()

    def _init_repo(self):
        subprocess.run(["git", "init"], cwd=self.repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Git Tutorial User"], cwd=self.repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "user@example.com"], cwd=self.repo_path, capture_output=True)
        subprocess.run(["git", "config", "init.defaultBranch", "main"], cwd=self.repo_path, capture_output=True)

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
