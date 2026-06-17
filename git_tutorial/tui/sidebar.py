from textual.widgets import Tree
from textual.message import Message

from ..content import discover_phases
from ..models import Phase, Topic


class TopicSelected(Message):
    def __init__(self, phase: Phase, topic: Topic) -> None:
        super().__init__()
        self.phase = phase
        self.topic = topic


class Sidebar(Tree):
    def __init__(self, **kwargs):
        super().__init__("Roadmap", **kwargs)
        self.progress = None
        self._phase_nodes = {}
        self._topic_nodes = {}
        self._phases = []
        self.root.expand()

    def load_phases(self) -> None:
        if not self.progress:
            return
        self.clear()
        self._phase_nodes = {}
        self._topic_nodes = {}
        self._phases = discover_phases()

        for phase in self._phases:
            unlocked = self.progress.is_phase_unlocked(phase.number)
            completed, total = self.progress.get_phase_progress(phase.number, len(phase.topics))

            if unlocked:
                bar_filled = "█" * completed
                bar_empty = "░" * (total - completed)
                progress_str = f"  [green]{bar_filled}[/][dim]{bar_empty}[/] {completed}/{total}"
                label = f"{phase.title}{progress_str}"
            else:
                label = f"[dim]{phase.title} (locked)[/]"

            branch = self.root.add(label, expand=False)
            self._phase_nodes[phase.number] = branch

            for topic in phase.topics:
                completed_topic = self.progress.is_complete(phase.number, topic.number)
                tlabel = f"{'[x]' if completed_topic else '[ ]'} {topic.title}"
                leaf = branch.add_leaf(tlabel)
                leaf.data = (phase, topic)
                self._topic_nodes[(phase.number, topic.number)] = leaf

    def on_tree_node_selected(self, event) -> None:
        node = event.node
        if node.data:
            phase, topic = node.data
            self.post_message(TopicSelected(phase, topic))
