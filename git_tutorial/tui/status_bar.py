from textual.widgets import Static, ProgressBar
from textual.widget import Widget
from textual.containers import Horizontal


class StatusHeader(Widget):
    def __init__(self, progress, **kwargs):
        super().__init__(**kwargs)
        self.progress = progress

    def compose(self):
        with Horizontal(id="status-container"):
            yield Static(id="status-level")
            yield Static(id="status-xp")
            yield ProgressBar(total=100, id="status-xp-bar", show_eta=False)
            yield Static(id="status-streak")
            yield Static(id="status-topics")
        with Horizontal(id="keybind-bar"):
            yield Static("[dim]q:Quit ?:Help Ctrl+B:Sidebar C:Content F5:Run[/]")
            yield Static(id="nav-hints", markup=True)

    def on_mount(self):
        self._update()

    def _update(self):
        level = self.progress.get_level()
        xp = self.progress.get_xp()
        info = self.progress.get_level_info()
        completed = self.progress.get_total_completed()
        streak = self.progress.get_streak()

        xp_progress = info["progress"]
        self.query_one("#status-level", Static).update(f"Lvl {level}")
        self.query_one("#status-xp", Static).update(f"XP {xp}/{info['xp_needed']}")
        self.query_one("#status-xp-bar", ProgressBar).progress = int(xp_progress * 100)
        self.query_one("#status-topics", Static).update(f"Topics {completed}")

        streak_text = f"Streak {streak}d" if streak else ""
        self.query_one("#status-streak", Static).update(streak_text)

    def update_nav(self, has_prev: bool, has_next: bool) -> None:
        hints = self.query_one("#nav-hints", Static)
        parts = []
        if has_prev:
            parts.append("[dim]Up:PrevT[/]")
        if has_next:
            parts.append("[dim]Down:NextT[/]")
        parts.append("[dim]Left:PrevS Right:NextS[/]")
        hints.update(" ".join(parts))

    def refresh(self, **kwargs):
        self._update()
        super().refresh(**kwargs)
