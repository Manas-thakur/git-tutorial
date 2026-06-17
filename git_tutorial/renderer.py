from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.box import ROUNDED
from rich.prompt import Prompt

from .models import Phase, Topic, Section


console = Console()


def show_banner():
    console.rule("[bold cyan]GIT TUTORIAL[/]", style="cyan")
    console.print("[dim]Learn Git from fundamentals to advanced workflows[/]", justify="center")
    console.print()


def show_phase_list(phases: list[Phase], progress, console: Console = console):
    table = Table(box=ROUNDED, title="[bold cyan]Git Roadmap[/]", title_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Phase", style="bold yellow", no_wrap=True)
    table.add_column("Topics", justify="right", width=8)
    table.add_column("Progress", width=22)

    for p in phases:
        done, total = progress.get_phase_progress(p.number, len(p.topics))
        bar = render_progress_bar(done, total, width=15)
        unlocked = progress.is_phase_unlocked(p.number)
        label = p.title if unlocked else f"{p.title} [dim](locked)[/]"
        table.add_row(str(p.number), label, f"{done}/{total}", bar)

    console.print(table)


def show_topic_list(phase: Phase, progress, console: Console = console):
    console.print(f"\n[bold cyan]Phase {phase.number}: {phase.title}[/]")
    console.print("[dim]" + "-" * console.width + "[/]")

    table = Table(box=ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Topic", style="bold white")
    table.add_column("Status", width=14)

    for t in phase.topics:
        status = "[green]Done[/]" if progress.is_complete(phase.number, t.number) else "[dim]Pending[/]"
        table.add_row(str(t.number), t.title, status)

    console.print(table)


def render_progress_bar(done: int, total: int, width: int = 20) -> str:
    if total == 0:
        return "[dim]-[/]"
    filled = int((done / total) * width) if total else 0
    bar = "█" * filled + "░" * (width - filled)
    return f"[green]{bar}[/]"


def show_topic_content(topic: Topic, console: Console = console):
    sections = topic.sections
    total = len(sections)

    console.print(f"\n[bold yellow]{topic.title}[/]")
    console.print("[dim]" + "-" * console.width + "[/]")

    for i, section in enumerate(sections, start=1):
        header = f"\n[{i}/{total}] {section.heading}"
        console.print(f"[bold cyan]{header}[/]")

        content_text = section.content.strip()
        if not content_text:
            console.print("[dim](no content)[/]")
            continue

        has_code = "```" in content_text

        if has_code:
            parts = content_text.split("```")
            for j, part in enumerate(parts):
                if j % 2 == 0:
                    if part.strip():
                        console.print(Markdown(part.strip()), width=console.width)
                else:
                    lines = part.splitlines()
                    lang = lines[0].strip() if lines else ""
                    code = "\n".join(lines[1:] if lang else lines)
                    if not lang:
                        lang = "bash"
                    try:
                        syntax = Syntax(code.strip(), lang, theme="monokai", line_numbers=False)
                        console.print(Panel(syntax, border_style="bright_blue"))
                    except Exception:
                        console.print(Panel(code.strip(), border_style="bright_blue"))
        else:
            md = Markdown(content_text)
            console.print(Panel(md, border_style="blue"))

        if i < total:
            Prompt.ask("[dim]Press Enter to continue[/]", default="")


def show_status(progress, console: Console = console):
    from .content import discover_phases
    phases = discover_phases()

    total_done = 0
    total_all = 0
    level_info = progress.get_level_info()

    console.print(f"\n[bold cyan]Learning Progress[/]")
    xp_bar = render_progress_bar(level_info["xp_current"], level_info["xp_needed"], 20)
    console.print(f"[bold]Level {level_info['level']}[/] {xp_bar} [dim]{level_info['xp_current']}/{level_info['xp_needed']} XP ({level_info['xp_total']} total)[/]")
    streak = progress.get_streak()
    if streak:
        console.print(f"[yellow]{streak}-day learning streak![/]")
    console.print(f"[dim]Progress saved to: {PROGRESS_FILE}[/]\n")

    table = Table(box=ROUNDED, header_style="bold magenta")
    table.add_column("Phase", style="bold yellow")
    table.add_column("Done", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Progress", width=30)

    for p in phases:
        done, total = progress.get_phase_progress(p.number, len(p.topics))
        total_done += done
        total_all += total
        bar = render_progress_bar(done, total, 25)
        table.add_row(f"Phase {p.number}: {p.title}", str(done), str(total), bar)

    bar = render_progress_bar(total_done, total_all, 25)
    table.add_row(
        "[bold]Total[/]", str(total_done), str(total_all), f"[bold]{bar}[/]"
    )
    console.print(table)

    pct = (total_done / total_all * 100) if total_all else 0
    if pct == 100:
        console.print("\n[bold green]All topics completed! You're a Git master![/]")
    else:
        remaining = total_all - total_done
        console.print(f"\n[cyan]Overall: {pct:.1f}% ({remaining} topics remaining)[/]")

    badges = progress.get_badges()
    if badges:
        render_badges(badges)


def render_badges(badges: list[dict], console: Console = console):
    if not badges:
        return
    console.print("\n[bold cyan]Your Badges[/]")
    for b in badges:
        console.print(f"  [bold]{b['name']}[/] - [dim]{b['desc']}[/]")


def render_quiz_result(correct: int, total: int, console: Console = console):
    pct = (correct / total) * 100 if total else 0
    color = "green" if pct >= 80 else "yellow" if pct >= 50 else "red"
    console.print()
    console.print(Panel(
        f"[bold]Score: [/{color}]{correct}/{total} ({pct:.0f}%)[/{color}][/]",
        title="[bold]Quiz Results[/]",
        border_style=color,
    ))
    console.print()


def render_completion(phase_num: int, topic_num: int, title: str, badges: list[dict] = None, xp_gained: int = 0, leveled_up: bool = False, console: Console = console):
    panel_content = f"[bold green]Topic Complete[/]\n\n[bold]{title}[/]"
    if xp_gained:
        level_text = " [bold yellow](LEVEL UP!)[/]" if leveled_up else ""
        panel_content += f"\n\n[bold]+{xp_gained} XP[/]{level_text}"
    if badges:
        earned = [b for b in badges if b["name"] in [x["name"] for x in (badges or [])]]
        if earned:
            badge_line = "  ".join(b["name"] for b in badges[-3:])
            panel_content += f"\n\n[bold yellow]Badges:[/]\n{badge_line}"
    console.print()
    console.print(Panel(
        panel_content,
        border_style="green",
    ))
    console.print()


from .progress import ProgressTracker, PROGRESS_FILE
