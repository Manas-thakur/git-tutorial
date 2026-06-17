from textual.widgets import Static, Markdown
from textual.containers import VerticalScroll
from textual.binding import Binding

from ..models import Topic


class ContentPanel(VerticalScroll):
    BINDINGS = [
        Binding("right", "next_section", "Next", show=False),
        Binding("left", "prev_section", "Prev", show=False),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._topic = None
        self._sections = []
        self._current_index = 0

    def compose(self):
        yield Static("", id="section-heading")
        yield Markdown("Select a topic from the sidebar", id="content-markdown")

    def load_topic(self, topic: Topic) -> None:
        self._topic = topic
        self._sections = topic.sections
        self._current_index = 0
        self._show_section()

    def _show_section(self) -> None:
        if not self._sections:
            self.query_one("#section-heading", Static).update("No sections")
            self.query_one("#content-markdown", Markdown).update("_No content available_")
            return

        section = self._sections[self._current_index]
        self.query_one("#section-heading", Static).update(
            f"[bold cyan][{self._current_index + 1}/{len(self._sections)}] {section.heading}[/]"
        )
        self.query_one("#content-markdown", Markdown).update(section.content)

    def action_next_section(self) -> None:
        if self._sections and self._current_index < len(self._sections) - 1:
            self._current_index += 1
            self._show_section()

    def action_prev_section(self) -> None:
        if self._sections and self._current_index > 0:
            self._current_index -= 1
            self._show_section()

    def clear(self) -> None:
        self._topic = None
        self._sections = []
        self._current_index = 0
        self.query_one("#content-markdown", Markdown).update("Select a topic from the sidebar")
        self.query_one("#section-heading", Static).update("")
