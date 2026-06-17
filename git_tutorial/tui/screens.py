from textual.screen import Screen, ModalScreen
from textual.widgets import Static, Button, Input, ListView, ListItem, Label, RichLog, DataTable
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from textual.binding import Binding

from ..content import discover_phases, get_quiz_questions


class QuizScreen(Screen):
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "next", "Next"),
        Binding("1", "answer_1", "A"),
        Binding("2", "answer_2", "B"),
        Binding("3", "answer_3", "C"),
        Binding("4", "answer_4", "D"),
    ]

    def __init__(self, progress, phase, **kwargs):
        super().__init__(**kwargs)
        self.progress = progress
        self.phase = phase
        self.questions = []
        self.current_index = 0
        self.correct = 0

    def compose(self) -> ComposeResult:
        yield Static("", id="quiz-header")
        yield Static("", id="quiz-question")
        yield Vertical(id="quiz-options")
        yield RichLog(id="quiz-feedback", highlight=True, markup=True)
        yield Static("", id="quiz-progress")
        yield Button("Close", id="close-quiz", variant="primary")

    def on_mount(self) -> None:
        for topic in self.phase.topics:
            self.questions.extend(get_quiz_questions(topic))
        if not self.questions:
            self.query_one("#quiz-header", Static).update("No quiz questions found")
            return
        self._show_question()

    def _show_question(self) -> None:
        if self.current_index >= len(self.questions):
            self._show_results()
            return

        q = self.questions[self.current_index]
        self.query_one("#quiz-header", Static).update(
            f"[bold cyan]Question {self.current_index + 1}/{len(self.questions)}[/]"
        )
        self.query_one("#quiz-question", Static).update(f"[bold yellow]{q.question}[/]")
        self.query_one("#quiz-progress", Static).update(
            f"Score: {self.correct}/{self.current_index}"
        )

        opts = self.query_one("#quiz-options", Vertical)
        opts.remove_children()

        if q.is_mcq:
            for i, opt in enumerate(q.options):
                opts.mount(Button(f"  {chr(65+i)}) {opt}", id=f"qopt-{i}"))
        else:
            opts.mount(Button("Reveal Answer", id="qopt-reveal", variant="default"))

        self.query_one("#quiz-feedback", RichLog).clear()

    def _show_results(self) -> None:
        self.query_one("#quiz-header", Static).update("[bold green]Quiz Complete![/]")
        self.query_one("#quiz-question", Static).update("")
        self.query_one("#quiz-options", Vertical).remove_children()
        fb = self.query_one("#quiz-feedback", RichLog)
        fb.clear()
        total = len(self.questions)
        fb.write(f"[bold]Final Score: {self.correct}/{total}[/]")
        if total > 0:
            pct = (self.correct / total) * 100
            fb.write(f"[bold]{pct:.0f}%[/]")
            self.progress.record_quiz_attempt(self.phase.number, 0, self.correct, total)
        self.query_one("#quiz-progress", Static).update("")

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_next(self) -> None:
        if self.current_index < len(self.questions):
            self.current_index += 1
            self._show_question()

    def action_answer_1(self) -> None:
        self._select_answer(0)

    def action_answer_2(self) -> None:
        self._select_answer(1)

    def action_answer_3(self) -> None:
        self._select_answer(2)

    def action_answer_4(self) -> None:
        self._select_answer(3)

    def _select_answer(self, idx: int) -> None:
        if not self.questions or self.current_index >= len(self.questions):
            return
        q = self.questions[self.current_index]
        if not q.is_mcq:
            return
        fb = self.query_one("#quiz-feedback", RichLog)
        if idx == q.answer_index:
            fb.write("[bold green]Correct![/]")
            self.correct += 1
        else:
            fb.write(f"[bold red]Incorrect.[/] Answer: {q.answer}")
        opts = self.query_one("#quiz-options", Vertical)
        opts.remove_children()
        opts.mount(Button("Next Question", id="qopt-next", variant="primary"))

    def on_button_pressed(self, event) -> None:
        if event.button.id == "close-quiz":
            self.action_close()
            return

        if not self.questions or self.current_index >= len(self.questions):
            return

        q = self.questions[self.current_index]

        if event.button.id == "qopt-reveal":
            fb = self.query_one("#quiz-feedback", RichLog)
            fb.write(f"[bold]Answer:[/] {q.answer}")
            opts = self.query_one("#quiz-options", Vertical)
            opts.remove_children()
            opts.mount(Button("Yes - got it right", id="qa-yes", variant="success"))
            opts.mount(Button("No - got it wrong", id="qa-no", variant="error"))

        elif event.button.id and event.button.id.startswith("qopt-"):
            try:
                choice = int(event.button.id.split("-")[1])
            except (ValueError, IndexError):
                return
            fb = self.query_one("#quiz-feedback", RichLog)
            if choice == q.answer_index:
                fb.write("[bold green]Correct![/]")
                self.correct += 1
            else:
                fb.write(f"[bold red]Incorrect.[/] Answer: {q.answer}")
            opts = self.query_one("#quiz-options", Vertical)
            opts.remove_children()
            opts.mount(Button("Next Question", id="qopt-next", variant="primary"))

        elif event.button.id == "qa-yes":
            self.correct += 1
            self.current_index += 1
            self._show_question()
        elif event.button.id == "qa-no":
            self.current_index += 1
            self._show_question()
        elif event.button.id == "qopt-next":
            self.current_index += 1
            self._show_question()


class SearchScreen(Screen):
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "open_selected", "Open"),
    ]

    def __init__(self, progress, **kwargs):
        super().__init__(**kwargs)
        self.progress = progress
        self._results = []

    def compose(self) -> ComposeResult:
        yield Static("[bold cyan]Search[/]", id="search-title")
        yield Input(placeholder="Type search term...", id="search-input")
        yield ListView(id="search-results")
        yield Button("Close", id="close-search", variant="primary")

    def on_input_changed(self, event) -> None:
        query = event.value.strip()
        listview = self.query_one("#search-results", ListView)
        listview.clear()
        self._results = []
        if not query:
            return
        phases = discover_phases()
        for p in phases:
            for t in p.topics:
                text = t.filepath.read_text(encoding="utf-8")
                if query.lower() in text.lower() or query.lower() in t.title.lower():
                    item = ListItem(Label(f"  P{p.number}.{t.number}  {t.title}"))
                    listview.append(item)
                    self._results.append((p, t))

    def action_open_selected(self) -> None:
        listview = self.query_one("#search-results", ListView)
        if listview.index is not None and listview.index < len(self._results):
            phase, topic = self._results[listview.index]
            self.dismiss((phase, topic))

    def action_close(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event) -> None:
        if event.button.id == "close-search":
            self.action_close()


class HelpScreen(ModalScreen):
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
        Binding("?", "close", "Close"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("[bold cyan]Keyboard Shortcuts[/]", id="help-title")
        yield DataTable(id="help-table")
        yield Button("Close", id="close-help", variant="primary")

    def on_mount(self) -> None:
        table = self.query_one("#help-table", DataTable)
        table.add_columns("Key", "Action")
        table.add_rows([
            ("q", "Quit tutorial"),
            ("F5", "Run git command"),
            ("Ctrl+P", "Search topics"),
            ("Ctrl+Q", "Start quiz"),
            ("r", "Reset progress"),
            ("Escape", "Close current screen"),
            ("Enter", "Confirm / Next question"),
            ("Left / Right", "Navigate sections"),
            ("1-4", "Select quiz answer"),
        ])

    def action_close(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event) -> None:
        if event.button.id == "close-help":
            self.action_close()
