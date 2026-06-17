from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.box import ROUNDED

from .models import Phase, Topic
from .content import (
    discover_phases,
    get_phase,
    get_topic,
    get_quiz_questions,
    search_content,
)
from .renderer import (
    console,
    show_banner,
    show_phase_list,
    show_topic_list,
    show_topic_content,
    show_status,
    render_completion,
    render_quiz_result,
    render_badges,
)
from .quiz import QuizEngine, run_flashcard_session
from .progress import ProgressTracker
from .sandbox import GitSandbox, sandbox_loop
from .challenges import get_challenges, get_next_challenge, run_challenge_setup, validate_challenge


app = typer.Typer(
    name="git-tutorial",
    help="Interactive Git tutorial: read, practice, quiz, and track progress",
    add_completion=False,
    rich_markup_mode="rich",
)
progress = ProgressTracker()

CONTENT_DIR_OPTION = typer.Option(
    None,
    "--content-dir",
    "-c",
    help="Path to the content directory (defaults to bundled content)",
    exists=True,
    file_okay=False,
    dir_okay=True,
    readable=True,
)


def _load_phases(content_dir: Optional[Path] = None) -> list[Phase]:
    return discover_phases(content_dir)


def _get_phase_or_exit(num: int, phases: list[Phase]) -> Phase:
    for p in phases:
        if p.number == num:
            return p
    console.print(f"[red]Phase {num} not found.[/]")
    raise typer.Exit(code=1)


def _get_topic_or_exit(phase: Phase, num: int) -> Topic:
    if num < 1 or num > len(phase.topics):
        console.print(f"[red]Topic {num} not found in Phase {phase.number}.[/]")
        raise typer.Exit(code=1)
    return phase.topics[num - 1]


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, content_dir: Optional[Path] = CONTENT_DIR_OPTION):
    """Git Interactive Tutorial - Learn Git from the terminal."""
    if ctx.invoked_subcommand is not None:
        return
    interactive_loop(content_dir)


def interactive_loop(content_dir: Optional[Path] = None):
    """Main interactive loop."""
    try:
        progress.add_streak()
        phases = _load_phases(content_dir)
        show_banner()
        _show_level_banner()

        bookmark = progress.get_bookmark()
        if bookmark:
            should_resume = Confirm.ask(
                f"[yellow]You were last viewing Phase {bookmark['phase']}, Topic {bookmark['topic']}. "
                "Resume?[/]",
                default=True,
            )
            if should_resume:
                phase = get_phase(bookmark["phase"], content_dir)
                if phase and bookmark["topic"] <= len(phase.topics):
                    topic = phase.topics[bookmark["topic"] - 1]
                    view_topic_content(bookmark["phase"], topic, content_dir)
                    progress.clear_bookmark()
                    return

        while True:
            show_phase_list(phases, progress)
            _show_global_hints()

            choice = Prompt.ask(
                "\n[bold]Select[/] [dim](phase#, search, flashcards, sandbox, badges, q)[/]",
                default="q",
            )

            if choice.lower() in ("q", "quit", "exit"):
                console.print("\n[dim]Happy committing![/]")
                break
            if choice.lower() in ("search", "s"):
                run_search(phases)
                continue
            if choice.lower() in ("flashcards", "fc"):
                run_flashcard_session()
                continue
            if choice.lower() in ("sandbox", "play"):
                with GitSandbox() as sb:
                    sb.create_initial_commit()
                    sandbox_loop(sb)
                continue
            if choice.lower() in ("progress", "p", "stats"):
                show_status(progress)
                continue
            if choice.lower() in ("badges",):
                render_badges(progress.get_badges())
                continue
            if choice.lower() in ("help",):
                show_help()
                continue

            if not choice.isdigit():
                continue
            phase_num = int(choice)
            phase = _get_phase_or_exit(phase_num, phases)

            if not progress.is_phase_unlocked(phase_num):
                prev_phase = next((p for p in phases if p.number == phase_num - 1), None)
                if prev_phase:
                    done, total = progress.get_phase_progress(phase_num - 1, len(prev_phase.topics))
                    pct = int(done / total * 100) if total else 0
                    console.print(f"[red]Phase is locked[/] - complete 70% of {prev_phase.title} first. [dim]({pct}% done)[/]")
                continue

            phase_menu(phase, content_dir)

    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Goodbye![/]")
        sys.exit(0)


def _show_level_banner():
    info = progress.get_level_info()
    bar = _bar(info["xp_current"], info["xp_needed"], 20)
    console.print(f"[bold]Level [cyan]{info['level']}[/]  {bar}  [dim]{info['xp_current']}/{info['xp_needed']} XP[/]")


def _show_global_hints():
    streak = progress.get_streak()
    streak_text = f" streak {streak}d" if streak else ""
    completed = progress.get_total_completed()
    level = progress.get_level()
    xp = progress.get_xp()
    total_topics = sum(len(p.topics) for p in discover_phases())
    console.print(f"[dim]{completed}/{total_topics} topics | Lv.{level} | {xp}XP{streak_text} | "
                  f"search, flashcards, sandbox, badges[/]")


def phase_menu(phase: Phase, content_dir: Optional[Path] = None):
    """Menu for a specific phase."""
    while True:
        show_topic_list(phase, progress)
        console.print("\n[dim]Options:[/]")
        console.print("  [bold]number[/] - View topic")
        console.print("  [bold]c <n>[/] - Do challenge for topic n")
        console.print("  [bold]quiz[/] - Take phase quiz")
        console.print("  [bold]flashcards[/] - Review phase flashcards")
        console.print("  [bold]sandbox[/] - Open git playground")
        console.print("  [bold]q[/] - Back")

        choice = Prompt.ask(f"\n[bold]Phase {phase.number}: {phase.title}[/]", default="q")

        if choice.lower() in ("q", "back"):
            break
        if choice.lower() == "quiz":
            run_phase_quiz(phase, content_dir)
            continue
        if choice.lower() == "flashcards":
            run_flashcard_session(phase.number)
            continue
        if choice.lower() == "sandbox":
            with GitSandbox() as sb:
                sb.create_initial_commit()
                sandbox_loop(sb)
            continue

        if choice.lower().startswith("c "):
            try:
                topic_num = int(choice.split()[1])
                topic = _get_topic_or_exit(phase, topic_num)
                run_challenge(phase.number, topic_num, topic.title)
            except (ValueError, IndexError):
                console.print("[red]Usage: c <topic_number>[/]")
            continue
        if choice.isdigit():
            topic_num = int(choice)
            topic = _get_topic_or_exit(phase, topic_num)
            view_topic_content(phase.number, topic, content_dir)
            progress.set_bookmark(phase.number, topic_num)
            progress.add_streak()


def view_topic_content(phase_num: int, topic: Topic, content_dir: Optional[Path] = None):
    """Display a topic section by section with quiz at the end."""
    show_topic_content(topic)

    quiz_questions = get_quiz_questions(topic)
    if quiz_questions:
        console.print("\n[bold cyan]Knowledge Check[/]")
        engine = QuizEngine()
        correct, total = engine.take_quiz(quiz_questions)
        if total > 0:
            render_quiz_result(correct, total)
            progress.record_quiz_attempt(phase_num, topic.number, correct, total)

    challenges = get_challenges(phase_num, topic.number)
    if challenges:
        do_challenge = Confirm.ask("\n[bold cyan]Try a Git challenge?[/]", default=True)
        if do_challenge:
            run_challenge(phase_num, topic.number, topic.title)

    xp_gained = 10
    if quiz_questions:
        xp_gained += 5
    if challenges:
        xp_gained += 5
    leveled_up = progress.add_xp(xp_gained)
    progress.mark_complete(phase_num, topic.number)
    badges = progress.get_badges()
    progress.add_streak()
    render_completion(phase_num, topic.number, topic.title, badges, xp_gained, leveled_up)


def run_challenge(phase_num: int, topic_num: int, title: str):
    """Run a git challenge for a topic."""
    challenges = get_challenges(phase_num, topic_num)
    if not challenges:
        console.print("[yellow]No challenges for this topic yet.[/]")
        console.print("[dim]Open 'sandbox' to practice on your own.[/]")
        return

    for idx, challenge in enumerate(challenges, start=1):
        if len(challenges) > 1:
            console.print(f"\n[bold cyan]Challenge {idx}/{len(challenges)}[/]")

        diff_color = {"easy": "green", "medium": "yellow", "hard": "red"}.get(challenge.difficulty, "cyan")
        console.print(Panel(
            f"[bold]{challenge.title}[/]  [{diff_color}]({challenge.difficulty})[/]\n\n{challenge.description}",
            border_style="cyan",
            title="[bold]Git Challenge[/]",
        ))

        do_setup = Confirm.ask("[dim]Run setup for this challenge?[/]", default=True)
        if not do_setup:
            console.print("[dim]Skipped.[/]")
            continue

        with GitSandbox() as sb:
            success = run_challenge_setup(challenge, sb)
            if not success:
                console.print("[red]Setup failed. Try the sandbox directly.[/]")
                continue

            console.print("\n[bold]Challenge ready![/] Complete the task, then type [bold]done[/] to validate.")
            console.print("[dim]Type 'hint' for help, 'skip' to move on[/]")

            while True:
                try:
                    cmd = input("  $ ")
                except EOFError:
                    break
                if cmd.strip().lower() == "done":
                    break
                if cmd.strip().lower() == "hint":
                    console.print(f"[yellow]Hint: {challenge.hint}[/]")
                    continue
                if cmd.strip().lower() == "skip":
                    console.print("[dim]Skipped.[/]")
                    break
                if not cmd.strip():
                    continue
                result = sb.run_command(cmd)
                if result["stdout"]:
                    console.print(result["stdout"].rstrip())
                if result["stderr"]:
                    console.print(f"[red]{result['stderr'].rstrip()}[/]")
            else:
                continue

            if validate_challenge(challenge, sb):
                xp_reward = {"easy": 15, "medium": 25, "hard": 40}.get(challenge.difficulty, 20)
                leveled_up = progress.add_xp(xp_reward)
                progress.mark_challenge_done(phase_num, topic_num, idx - 1)
                level_notice = " [yellow]LEVEL UP![/]" if leveled_up else ""
                console.print(f"[bold green]Challenge passed! +{xp_reward}XP{level_notice}[/]")
            else:
                console.print("[bold yellow]Not quite right. Try again in sandbox mode.[/]")

    console.print("[bold green]All challenges complete for this topic![/]")


def run_phase_quiz(phase: Phase, content_dir: Optional[Path] = None):
    """Quiz across all topics in a phase."""
    all_questions = []
    for topic in phase.topics:
        questions = get_quiz_questions(topic)
        all_questions.extend(questions)

    if not all_questions:
        console.print("[yellow]No quiz questions found in this phase.[/]")
        return

    console.print(Panel(
        f"[bold cyan]Phase Quiz: {phase.title}[/]\n\n"
        f"[bold]{len(all_questions)} questions across {len(phase.topics)} topics[/]",
        border_style="cyan",
    ))
    engine = QuizEngine()
    correct, total = engine.take_quiz(all_questions)
    render_quiz_result(correct, total)
    if total > 0:
        progress.add_xp(5)


# ---- CLI Commands ----


@app.command()
def list(content_dir: Optional[Path] = CONTENT_DIR_OPTION):
    """List all phases and their topics."""
    show_banner()
    phases = _load_phases(content_dir)
    show_phase_list(phases, progress)


@app.command()
def view(
    phase: int = typer.Argument(..., help="Phase number"),
    topic: int = typer.Argument(..., help="Topic number"),
    content_dir: Optional[Path] = CONTENT_DIR_OPTION,
):
    """View a specific topic by phase and topic number."""
    phases = _load_phases(content_dir)
    p = _get_phase_or_exit(phase, phases)
    t = _get_topic_or_exit(p, topic)
    view_topic_content(phase, t, content_dir)


@app.command()
def practice(
    phase: int = typer.Argument(..., help="Phase number"),
    topic: int = typer.Argument(..., help="Topic number"),
    content_dir: Optional[Path] = CONTENT_DIR_OPTION,
):
    """Open sandbox with practice exercises for a topic."""
    phases = _load_phases(content_dir)
    p = _get_phase_or_exit(phase, phases)
    t = _get_topic_or_exit(p, topic)
    console.print(f"[bold cyan]Practice: {t.title}[/]")
    challenges = get_challenges(phase, topic)
    if challenges:
        console.print("[bold]Available challenges for this topic:[/]")
        for i, c in enumerate(challenges, 1):
            console.print(f"  {i}. {c.title} [dim]({c.difficulty})[/]")
        console.print()
    with GitSandbox() as sb:
        sb.create_initial_commit()
        sandbox_loop(sb)


@app.command()
def quiz(
    phase: int = typer.Argument(None, help="Phase number (optional - all phases if omitted)"),
    content_dir: Optional[Path] = CONTENT_DIR_OPTION,
):
    """Take a quiz for a phase or all phases."""
    phases = _load_phases(content_dir)

    if phase is not None:
        p = _get_phase_or_exit(phase, phases)
        run_phase_quiz(p, content_dir)
        return

    all_q = []
    for p in phases:
        for t in p.topics:
            all_q.extend(get_quiz_questions(t))

    console.print(Panel(
        f"[bold cyan]Full Git Quiz[/]\n\n"
        f"[bold]{len(all_q)} questions across all phases[/]",
        border_style="cyan",
    ))
    engine = QuizEngine()
    correct, total = engine.take_quiz(all_q)
    render_quiz_result(correct, total)


@app.command()
def flashcards(
    phase: int = typer.Argument(None, help="Phase number (optional)"),
):
    """Review flashcards for a phase or all phases."""
    run_flashcard_session(phase)


@app.command()
def challenge(
    phase: int = typer.Argument(None, help="Phase number"),
    topic: int = typer.Argument(None, help="Topic number"),
    content_dir: Optional[Path] = CONTENT_DIR_OPTION,
):
    """Run a Git challenge for a specific topic."""
    phases = _load_phases(content_dir)
    if phase is None:
        console.print("[bold cyan]Available Challenges[/]")
        from .challenges import CHALLENGES
        table = Table(box=ROUNDED, header_style="bold magenta")
        table.add_column("Phase", style="bold yellow")
        table.add_column("Topic", style="bold white")
        table.add_column("Challenge", style="cyan")
        table.add_column("Difficulty")
        for c in CHALLENGES:
            phase_obj = get_phase(c.phase, content_dir)
            topic_obj = get_topic(c.phase, c.topic, content_dir)
            topic_name = topic_obj.title if topic_obj else f"Topic {c.topic}"
            diff_color = {"easy": "green", "medium": "yellow", "hard": "red"}.get(c.difficulty, "cyan")
            table.add_row(
                phase_obj.title if phase_obj else f"Phase {c.phase}",
                topic_name,
                c.title,
                f"[{diff_color}]{c.difficulty}[/{diff_color}]",
            )
        console.print(table)
        return

    p = _get_phase_or_exit(phase, phases)
    if topic is None:
        console.print("[yellow]Usage: challenge <phase> <topic>[/]")
        return
    t = _get_topic_or_exit(p, topic)
    run_challenge(phase, topic, t.title)


@app.command()
def sandbox():
    """Open the interactive Git sandbox."""
    with GitSandbox() as sb:
        sb.create_initial_commit()
        sandbox_loop(sb)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search term"),
    content_dir: Optional[Path] = CONTENT_DIR_OPTION,
):
    """Search across all topics for a keyword."""
    phases = _load_phases(content_dir)
    run_search(phases, query)


def run_search(phases: list[Phase], query: str = None):
    """Interactive search across all topics."""
    if not query:
        query = Prompt.ask("[bold]Search for[/]")
    if not query or not query.strip():
        return
    query = query.strip()
    results = search_content(query, phases)

    if not results:
        console.print(f"[yellow]No results found for '{query}'[/]")
        return

    console.print(f"\n[bold cyan]Search results for '{query}'[/] ({len(results)} topics)")
    for r in results[:15]:
        console.print(f"\n[bold yellow]P{r['phase']}.{r['topic']}[/] {r['title']}")
        for line_no, text in r["matches"][:5]:
            truncated = text[:100] + "..." if len(text) > 100 else text
            console.print(f"  [dim]L{line_no}:[/] {truncated}")

    if results:
        view_one = Prompt.ask(
            "[bold]View a topic? (phase.topic or Enter to skip)[/]", default=""
        )
        if view_one and "." in view_one:
            try:
                pn, tn = view_one.split(".")
                p = _get_phase_or_exit(int(pn), phases)
                t = _get_topic_or_exit(p, int(tn))
                view_topic_content(int(pn), t)
            except (ValueError, typer.Exit):
                pass


@app.command()
def status(content_dir: Optional[Path] = CONTENT_DIR_OPTION):
    """Show your learning progress, streak, and badges."""
    show_status(progress)


@app.command()
def badges():
    """Show earned badges."""
    render_badges(progress.get_badges())


def show_help():
    """Display keybindings and command reference."""
    console.print(Panel(
        "[bold cyan]Git Tutorial - Commands[/]\n\n"
        "[bold]CLI Commands:[/]\n"
        "  [bold]list[/]              - List all phases and topics\n"
        "  [bold]view[/] <p> <t>      - View a specific topic\n"
        "  [bold]practice[/] <p> <t>  - Open sandbox with practice\n"
        "  [bold]quiz[/] [phase]      - Take a quiz\n"
        "  [bold]flashcards[/] [ph]   - Flashcard review\n"
        "  [bold]challenge[/] [p] [t] - Git challenges\n"
        "  [bold]sandbox[/]           - Open Git playground\n"
        "  [bold]search[/] <query>    - Search content\n"
        "  [bold]status[/]            - Show progress\n"
        "  [bold]badges[/]            - Show badges\n"
        "  [bold]bookmark[/]          - Show bookmark\n"
        "  [bold]reset[/]             - Reset all progress\n"
        "  [bold]help[/]              - This help screen\n"
        "  [bold]interactive[/]       - Launch interactive mode\n\n"
        "[bold]Interactive Mode:[/]\n"
        "  [bold]<number>[/]           - Select a phase\n"
        "  [bold]search[/] / [bold]s[/]      - Search topics\n"
        "  [bold]flashcards[/] / [bold]fc[/] - Flashcard mode\n"
        "  [bold]sandbox[/] / [bold]play[/]  - Open sandbox\n"
        "  [bold]badges[/]             - View badges\n"
        "  [bold]q[/] / [bold]quit[/]       - Exit\n\n"
        "[bold]Reading a Topic:[/]\n"
        "  Press Enter to advance through sections\n"
        "  Quiz and challenges appear at the end\n\n"
        "[bold]In Sandbox:[/]\n"
        "  [bold]init[/]     - Create initial commit with README\n"
        "  [bold]exit[/]     - Return to tutorial\n"
        "  [bold]Ctrl+D[/]   - Exit sandbox\n\n"
        "[bold]In Challenge:[/]\n"
        "  [bold]done[/]     - Validate your work\n"
        "  [bold]hint[/]     - Show a hint\n"
        "  [bold]skip[/]     - Skip to next challenge",
        border_style="cyan",
        title="[bold]Help & Keybindings[/]",
    ))


@app.command()
def reset():
    """Reset all progress."""
    if Confirm.ask("[red]This will delete ALL progress. Are you sure?[/]"):
        progress.reset()
        console.print("[green]Progress reset successfully.[/]")


@app.command()
def bookmark():
    """Show your current bookmark."""
    bm = progress.get_bookmark()
    if bm:
        console.print(f"[yellow]Bookmark: Phase {bm['phase']}, Topic {bm['topic']}[/]")
    else:
        console.print("[dim]No bookmark set.[/]")


@app.command()
def interactive(content_dir: Optional[Path] = CONTENT_DIR_OPTION):
    """Launch the interactive mode."""
    interactive_loop(content_dir)


def _bar(done: int, total: int, width: int) -> str:
    if total == 0:
        return "░" * width
    filled = int((done / total) * width)
    return "█" * filled + "░" * (width - filled)

