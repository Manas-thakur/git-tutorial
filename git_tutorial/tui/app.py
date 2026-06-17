from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static, Button, Label
from textual.containers import Container

from ..progress import ProgressTracker
from ..sandbox import GitSandbox
from .sidebar import Sidebar, TopicSelected
from .content_panel import ContentPanel
from .terminal_panel import TerminalPanel
from .status_bar import StatusHeader
from .screens import QuizScreen, SearchScreen, HelpScreen


class ConfirmScreen(Screen):
    def __init__(self, title: str, message: str, callback):
        super().__init__()
        self._title = title
        self._message = message
        self._callback = callback

    def compose(self):
        yield Static(f"[bold yellow]{self._title}[/]", id="confirm-title")
        yield Label(self._message, id="confirm-message")
        with Container(id="confirm-buttons"):
            yield Button("Yes", id="confirm-yes", variant="error")
            yield Button("No", id="confirm-no", variant="primary")

    def on_button_pressed(self, event):
        self._callback(event.button.id == "confirm-yes")
        self.app.pop_screen()


class MainContainer(Container):
    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield ContentPanel()
        yield TerminalPanel(self._sandbox)

    def __init__(self, sandbox: GitSandbox | None = None):
        super().__init__()
        self._sandbox = sandbox


class TutorialApp(App):
    CSS = """
    MainContainer {
        layout: horizontal;
        height: 1fr;
    }

    MainContainer > Sidebar {
        width: 25%;
        height: 100%;
        border: solid $primary;
    }

    MainContainer > ContentPanel {
        width: 40%;
        height: 100%;
        border: solid $secondary;
    }

    ContentPanel {
        layout: vertical;
        height: 100%;
    }

    ContentPanel > #section-heading {
        height: auto;
    }

    ContentPanel > Markdown {
        width: 100%;
        height: auto;
    }

    MainContainer > TerminalPanel {
        width: 35%;
        height: 100%;
        border: solid $accent;
    }

    StatusHeader {
        dock: bottom;
        height: 1;
    }

    StatusHeader > #status-container {
        height: 1;
    }

    #status-container > Static {
        margin: 0 1;
    }

    #status-container > ProgressBar {
        width: 15;
    }

    #title-bar {
        dock: top;
        height: 1;
        background: $primary;
        color: $text;
        text-style: bold;
        text-align: center;
    }

    ConfirmScreen {
        align: center middle;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("f5", "run_command", "Run", show=True),
        Binding("ctrl+p", "search", "Search", show=True),
        Binding("ctrl+q", "quiz", "Quiz", show=True),
        Binding("r", "reset_progress", "Reset", show=False),
        Binding("?", "help", "Help", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.progress = ProgressTracker()
        self.sandbox = GitSandbox()
        self.current_phase = None
        self.current_topic = None

    def compose(self) -> ComposeResult:
        yield Static("[bold]Git Interactive Tutorial[/]", id="title-bar")
        yield MainContainer(self.sandbox)
        yield StatusHeader(self.progress)

    def on_mount(self) -> None:
        self.title = "Git Interactive Tutorial"
        self.progress.add_streak()
        sidebar = self.query_one(Sidebar)
        sidebar.progress = self.progress
        sidebar.load_phases()

    def action_quit(self) -> None:
        self.sandbox.cleanup()
        self.exit()

    def action_run_command(self) -> None:
        self.query_one(TerminalPanel).action_run_command()

    def action_search(self) -> None:
        self.push_screen(SearchScreen(self.progress), self._on_search_selected)

    def _on_search_selected(self, result) -> None:
        if result:
            phase, topic = result
            self._load_topic(phase, topic)

    def action_quiz(self) -> None:
        if self.current_phase:
            self.push_screen(QuizScreen(self.progress, self.current_phase))

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_reset_progress(self) -> None:
        def on_confirm(confirmed: bool):
            if confirmed:
                self.progress.reset()
                self.query_one(Sidebar).load_phases()
                self.query_one(ContentPanel).clear()
                self.query_one(TerminalPanel).clear_output()
                self.query_one(StatusHeader).refresh()
        self.push_screen(
            ConfirmScreen("Reset Progress", "This will delete ALL progress. Are you sure?", on_confirm)
        )

    def on_topic_selected(self, message: TopicSelected) -> None:
        self._load_topic(message.phase, message.topic)

    def _load_topic(self, phase, topic) -> None:
        self.current_phase = phase
        self.current_topic = topic
        self.query_one(ContentPanel).load_topic(topic)
        self.query_one(TerminalPanel).load_topic(topic)
        self.progress.set_bookmark(phase.number, topic.number)
        self.query_one(StatusHeader).refresh()


def main():
    app = TutorialApp()
    app.run()
