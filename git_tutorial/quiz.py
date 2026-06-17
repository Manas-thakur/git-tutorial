from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from .models import QuizQuestion
from .content import get_quiz_questions, discover_phases


console = Console()


class QuizEngine:
    def load_questions(self, phases: list = None) -> list[QuizQuestion]:
        if phases is None:
            from .content import discover_phases
            phases = discover_phases()
        questions = []
        for p in phases:
            for t in p.topics:
                questions.extend(get_quiz_questions(t))
        return questions

    def take_quiz(self, questions: list[QuizQuestion], console: Console = console) -> tuple[int, int]:
        if not questions:
            console.print("[yellow]No quiz questions available.[/]")
            return 0, 0

        correct = 0
        total = len(questions)

        console.print(Panel(
            "[bold cyan]Knowledge Check[/]\n\n"
            "Test your understanding of Git.",
            border_style="cyan",
        ))

        for i, q in enumerate(questions, start=1):
            console.print(f"\n[bold yellow]Q{i}.[/] {q.question}")

            if q.is_mcq:
                for j, opt in enumerate(q.options, start=1):
                    console.print(f"  [dim]{j}.[/] {opt}")
                answer = Prompt.ask(
                    "[bold]Your answer[/]",
                    choices=[str(k) for k in range(1, len(q.options) + 1)],
                    default="1",
                )
                choice = int(answer) - 1
                if choice == q.answer_index:
                    console.print("  [bold green]Correct![/]")
                    correct += 1
                else:
                    console.print(f"  [bold red]Incorrect.[/] The answer was: [green]{q.answer}[/]")
            else:
                console.print("[dim]Press Enter when ready to see the answer...[/]")
                Prompt.ask("", default="")
                console.print(f"  [bold]Answer:[/] [green]{q.answer}[/]")
                ok = Prompt.ask("[bold]Did you get it right? (y/n)[/]", default="y")
                if ok.strip().lower() == "y":
                    correct += 1

        return correct, total

    def run_flashcard_session(self, questions: list[QuizQuestion], console: Console = console):
        if not questions:
            console.print("[yellow]No flashcards available.[/]")
            return

        console.print(Panel(
            "[bold cyan]Flashcard Review[/]\n\n"
            "Read the question, think of the answer, then reveal.\n"
            "Rate your recall to track mastery.",
            border_style="cyan",
        ))

        import random
        random.shuffle(questions)

        reviewed = 0
        known = 0

        for q in questions:
            reviewed += 1
            console.print(f"\n[bold yellow]Card {reviewed}/{len(questions)}[/]")
            console.print(f"[bold]{q.question}[/]")

            if q.is_mcq:
                for j, opt in enumerate(q.options, start=1):
                    console.print(f"  [dim]{j}.[/] {opt}")
                answer = Prompt.ask(
                    "[bold]Your answer[/]",
                    choices=[str(k) for k in range(1, len(q.options) + 1)],
                    default="1",
                )
                choice = int(answer) - 1
                if choice == q.answer_index:
                    console.print("  [bold green]Correct![/]")
                    known += 1
                else:
                    console.print(f"  [bold red]Incorrect.[/] The answer was: [green]{q.answer}[/]")
            else:
                Prompt.ask("[dim]Press Enter to reveal the answer[/]", default="")
                console.print(f"  [bold]Answer:[/] [green]{q.answer}[/]")
                knew = Prompt.ask("[bold]Did you know this? (y/n)[/]", default="y")
                if knew.strip().lower() == "y":
                    known += 1

            if reviewed < len(questions):
                Prompt.ask("[dim]Press Enter for next card[/]", default="")

        console.print()
        pct = (known / reviewed) * 100 if reviewed else 0
        color = "green" if pct >= 80 else "yellow" if pct >= 50 else "red"
        console.print(Panel(
            f"[bold]Flashcard session complete.[/]\n\n"
            f"[bold]Known: [/{color}]{known}/{reviewed} ({pct:.0f}%)[/{color}][/]",
            border_style=color,
        ))
        console.print()


def run_quiz(questions: list[QuizQuestion]) -> tuple[int, int]:
    engine = QuizEngine()
    return engine.take_quiz(questions)


def run_flashcard_session(phase_number: int = None):
    from .content import discover_phases, get_quiz_questions
    phases = discover_phases()
    questions = []
    for p in phases:
        if phase_number is not None and p.number != phase_number:
            continue
        for t in p.topics:
            questions.extend(get_quiz_questions(t))
    engine = QuizEngine()
    engine.run_flashcard_session(questions)
