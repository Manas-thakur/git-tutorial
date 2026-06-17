from textual.widgets import Static, Input, RichLog, Button
from textual.widget import Widget
from textual.containers import Horizontal
from textual.binding import Binding

from ..sandbox import GitSandbox


class TerminalPanel(Widget):
    BINDINGS = [
        Binding("f5", "run_command", "Run", show=False),
    ]

    def __init__(self, sandbox: GitSandbox | None = None, **kwargs):
        super().__init__(**kwargs)
        self.sandbox = sandbox or GitSandbox()
        self._topic = None

    def compose(self):
        yield Static("[bold]Git Terminal[/]", id="terminal-heading")
        yield Input(placeholder="Type a git command...", id="cmd-input")
        yield RichLog(id="output-log", highlight=True, markup=True, max_lines=100)
        with Horizontal(id="terminal-buttons"):
            yield Button("Run (F5)", id="run-btn", variant="primary")
            yield Button("Clear", id="clear-btn", variant="default")

    def action_run_command(self) -> None:
        cmd_input = self.query_one("#cmd-input", Input)
        log = self.query_one("#output-log", RichLog)
        cmd = cmd_input.value.strip()
        if not cmd:
            log.write("[dim]No command entered[/]")
            return
        log.write(f"[dim]$ {cmd}[/]")
        result = self.sandbox.run_command(cmd)
        if result["stdout"]:
            log.write(result["stdout"].rstrip())
        if result["stderr"]:
            log.write(f"[red]{result['stderr'].rstrip()}[/]")
        if result["success"] and not result["stdout"]:
            log.write("[green]Command executed successfully[/]")
        elif not result["success"] and not result["stderr"]:
            log.write("[red]Command failed[/]")
        cmd_input.clear()

    def clear_output(self) -> None:
        self.query_one("#output-log", RichLog).clear()

    def load_topic(self, topic) -> None:
        self._topic = topic
        self.query_one("#terminal-heading", Static).update(f"[bold]Git Terminal - {topic.title}[/]")

    def load_example_command(self, cmd: str) -> None:
        self.query_one("#cmd-input", Input).value = cmd

    def on_button_pressed(self, event) -> None:
        if event.button.id == "run-btn":
            self.action_run_command()
        elif event.button.id == "clear-btn":
            self.clear_output()

    def on_input_submitted(self, event) -> None:
        self.action_run_command()
