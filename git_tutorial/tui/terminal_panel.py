from textual.widgets import Static, Input, RichLog, Button
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding
from textual.suggester import Suggester

from ..sandbox import GitSandbox, GIT_COMMANDS
from ..scenario import get_scenario, setup_scenario, validate_step, Scenario


class GitSuggester(Suggester):
    def __init__(self, sandbox: GitSandbox):
        super().__init__()
        self.sandbox = sandbox

    async def get_suggestion(self, value: str) -> str | None:
        try:
            if not value.strip():
                return None
            parts = value.strip().split()
            if len(parts) == 1 and not value.strip().endswith(" "):
                prefix = parts[0].lower()
                matches = [c for c in GIT_COMMANDS if c.startswith(prefix)]
                if len(matches) == 1:
                    return f"git {matches[0]} "
                return None
            if len(parts) >= 2 and parts[0].lower() in ("git",):
                subcmd = parts[1].lower()
                typed = parts[-1].lower() if not value.endswith(" ") else ""
                if subcmd in ("switch", "checkout", "branch", "merge") and typed:
                    branches = self.sandbox.get_branches()
                    matches = [b for b in branches if b.startswith(typed)]
                    if len(matches) == 1:
                        base = " ".join(parts[:-1]) + " "
                        return f"{base}{matches[0]}"
        except Exception:
            pass
        return None


class TerminalPanel(Container):
    BINDINGS = [
        Binding("f5", "run_command", "Run", show=False),
        Binding("f6", "run_status", "Status", show=False),
        Binding("f7", "run_log", "Log", show=False),
        Binding("f8", "run_diff", "Diff", show=False),
        Binding("f9", "show_graph", "Graph", show=False),
        Binding("tab", "autocomplete", "Complete", show=False),
    ]

    def __init__(self, sandbox: GitSandbox | None = None, **kwargs):
        super().__init__(**kwargs)
        self.sandbox = sandbox or GitSandbox()
        self._topic = None
        self._scenario: Scenario | None = None
        self._scenario_active = False
        self._completed_steps: set[int] = set()
        self._current_step = 0
        self._history: list[str] = []
        self._history_index = -1

    def compose(self):
        with Vertical(id="terminal-container"):
            yield Static("[bold]Git Terminal[/]", id="terminal-heading")
            yield Static("", id="scenario-header")
            yield Input(
                placeholder="Type a git command...",
                id="cmd-input",
                suggester=GitSuggester(self.sandbox),
            )
            with Horizontal(id="shortcut-hints"):
                yield Static("[dim]F5:Run F6:Status F7:Log F8:Diff F9:Graph[/]")
            yield RichLog(id="output-log", highlight=True, markup=True, max_lines=200)
            with Horizontal(id="terminal-buttons"):
                yield Button("Run (F5)", id="run-btn", variant="primary")
                yield Button("Graph", id="graph-btn", variant="default")
                yield Button("Clear", id="clear-btn", variant="default")
                yield Button("History", id="history-btn", variant="default")
                yield Button("Reset Repo", id="reset-btn", variant="error")

    def _show_scenario(self) -> None:
        header = self.query_one("#scenario-header", Static)
        if not self._scenario:
            header.update("")
            return
        if not self._scenario_active:
            header.update(f"[bold cyan]Scenario: {self._scenario.title}[/]\n{self._scenario.goal}")
            return
        step = self._scenario.steps[self._current_step] if self._current_step < len(self._scenario.steps) else None
        if step:
            header.update(
                f"[bold cyan]Scenario: {self._scenario.title}[/]\n"
                f"[green]Step {self._current_step + 1}/{len(self._scenario.steps)}:[/] {step.description}"
            )
        else:
            header.update("[bold green]Scenario complete![/]")

    def on_mount(self) -> None:
        self.query_one("#cmd-input", Input).focus()

    def load_topic(self, topic, phase_number: int = 1) -> None:
        self._topic = topic
        self._scenario = get_scenario(phase_number, topic.number)
        self._scenario_active = False
        self._completed_steps = set()
        self._current_step = 0
        heading = self.query_one("#terminal-heading", Static)
        heading.update(f"[bold]Git Terminal - {topic.title}[/]")
        if self._scenario:
            self.sandbox.reset_repo()
            self._show_scenario()
            self._show_graph_auto()

    def action_run_command(self) -> None:
        cmd_input = self.query_one("#cmd-input", Input)
        log = self.query_one("#output-log", RichLog)
        cmd = cmd_input.value.strip()
        if not cmd:
            log.write("[dim]No command entered[/]")
            return

        self._history.append(cmd)
        self._history_index = len(self._history)

        if cmd.lower() in ("done", "complete"):
            if self._scenario and self._scenario_active:
                log.write("[bold green]Scenario marked as done![/]")
            return

        if cmd.lower() == "reset":
            self.sandbox.reset_repo()
            log.write("[bold yellow]Repository reset to clean state[/]")
            self._show_graph_auto()
            cmd_input.clear()
            return

        if cmd.lower().startswith("git help"):
            from ..scenario import SCENARIOS
            log.write("[bold]Available scenarios:[/]")
            for key, s in SCENARIOS.items():
                log.write(f"  Phase {s.phase}.{s.topic}: {s.title} - {s.goal}")
            cmd_input.clear()
            return

        log.write(f"[dim]$ {cmd}[/]")
        result = self.sandbox.run_command(cmd)

        if result["stdout"]:
            log.write(result["stdout"].rstrip())
        if result["stderr"]:
            log.write(f"[red]{result['stderr'].rstrip()}[/]")
        if result["success"] and not result["stdout"] and not result["stderr"]:
            log.write("[green]Command executed successfully[/]")
        elif not result["success"] and not result["stderr"]:
            log.write("[red]Command failed[/]")

        if self._scenario:
            if not self._scenario_active:
                setup_scenario(self.sandbox, self._scenario)
                self._scenario_active = True
                result = self.sandbox.run_command(cmd)
                if result["stdout"]:
                    log.write(result["stdout"].rstrip())
                if result["stderr"]:
                    log.write(f"[red]{result['stderr'].rstrip()}[/]")
            self._check_scenario_progress(cmd, log)

        self._show_graph_auto()
        cmd_input.clear()

    def _check_scenario_progress(self, cmd: str, log: RichLog) -> None:
        if not self._scenario_active:
            self._scenario_active = True
        if self._current_step >= len(self._scenario.steps):
            return
        ok, msg = validate_step(cmd, self._scenario, self._current_step)
        if ok:
            self._completed_steps.add(self._current_step)
            self._current_step += 1
            log.write(msg)
            if self._current_step >= len(self._scenario.steps):
                log.write("[bold green]Scenario complete! Great work.[/]")
        else:
            log.write(msg)
        self._show_scenario()

    def _show_graph_auto(self) -> None:
        try:
            log = self.query_one("#output-log", RichLog)
            graph = self.sandbox.get_graph()
            log.write("")
            log.write(graph)
        except Exception:
            pass

    def action_run_status(self) -> None:
        log = self.query_one("#output-log", RichLog)
        log.write("[bold cyan]--- Status ---[/]")
        status = self.sandbox.get_status()
        log.write(status)

    def action_run_log(self) -> None:
        log = self.query_one("#output-log", RichLog)
        log.write("[bold cyan]--- Log ---[/]")
        r = self.sandbox.run_command("git log --oneline --graph --all --decorate -40")
        if r["success"] and r["stdout"]:
            log.write(r["stdout"].rstrip())
        else:
            log.write("[dim](no commits yet)[/]")

    def action_run_diff(self) -> None:
        log = self.query_one("#output-log", RichLog)
        log.write("[bold cyan]--- Diff ---[/]")
        diff = self.sandbox.get_diff()
        log.write(diff)

    def action_show_graph(self) -> None:
        log = self.query_one("#output-log", RichLog)
        log.write("[bold cyan]--- Commit Graph ---[/]")
        self._show_graph_auto()

    def show_history(self) -> None:
        log = self.query_one("#output-log", RichLog)
        log.write("[bold cyan]--- Command History ---[/]")
        if not self._history:
            log.write("[dim](no commands yet)[/]")
            return
        for i, cmd in enumerate(self._history, 1):
            log.write(f"  {i}. {cmd}")

    def action_autocomplete(self) -> None:
        cmd_input = self.query_one("#cmd-input", Input)
        val = cmd_input.value.strip()
        if not val:
            return
        parts = val.split()
        if len(parts) == 1:
            prefix = parts[0].lower()
            matches = [c for c in GIT_COMMANDS if c.startswith(prefix)]
            if len(matches) == 1:
                cmd_input.value = f"git {matches[0]} "
                cmd_input.cursor_position = len(cmd_input.value)
            elif len(matches) > 1:
                log = self.query_one("#output-log", RichLog)
                log.write(f"[dim]Commands: {', '.join(matches)}[/]")

    def on_input_submitted(self, event) -> None:
        self.action_run_command()

    def on_button_pressed(self, event) -> None:
        if event.button.id == "run-btn":
            self.action_run_command()
        elif event.button.id == "graph-btn":
            self.action_show_graph()
        elif event.button.id == "clear-btn":
            self.query_one("#output-log", RichLog).clear()
        elif event.button.id == "history-btn":
            self.show_history()
        elif event.button.id == "reset-btn":
            self.sandbox.reset_repo()
            log = self.query_one("#output-log", RichLog)
            log.write("[bold yellow]Repository reset to clean state[/]")
            self._show_graph_auto()

    def clear_output(self) -> None:
        self.query_one("#output-log", RichLog).clear()

    def load_example_command(self, cmd: str) -> None:
        self.query_one("#cmd-input", Input).value = cmd
