import pytest

from git_tutorial.tui.app import TutorialApp, MainContainer
from git_tutorial.tui.sidebar import Sidebar
from git_tutorial.tui.content_panel import ContentPanel
from git_tutorial.tui.terminal_panel import TerminalPanel
from git_tutorial.tui.status_bar import StatusHeader
from git_tutorial.tui.screens import CheatSheetScreen, HelpScreen, SearchScreen
from git_tutorial.session import STATE_FILE


@pytest.fixture(autouse=True)
def clear_session():
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    yield


async def _defocus_input(pilot):
    """Move focus away from the cmd-input by focusing the sidebar."""
    from git_tutorial.tui.sidebar import Sidebar
    sidebar = pilot.app.query_one(Sidebar)
    sidebar.focus()


@pytest.mark.asyncio
async def test_app_starts():
    async with TutorialApp().run_test(size=(120, 40)) as pilot:
        app = pilot.app
        assert app.title == "Git Interactive Tutorial"
        assert app.query_one(Sidebar) is not None
        assert app.query_one(ContentPanel) is not None
        assert app.query_one(TerminalPanel) is not None
        assert app.query_one(StatusHeader) is not None


@pytest.mark.asyncio
async def test_sidebar_not_collapsed_by_default():
    async with TutorialApp().run_test(size=(120, 40)) as pilot:
        app = pilot.app
        assert not app.sidebar_collapsed
        main = app.query_one(MainContainer)
        assert "sidebar-collapsed" not in main.classes


@pytest.mark.asyncio
async def test_content_not_collapsed_by_default():
    async with TutorialApp().run_test(size=(120, 40)) as pilot:
        app = pilot.app
        assert not app.content_collapsed
        main = app.query_one(MainContainer)
        assert "content-collapsed" not in main.classes


@pytest.mark.asyncio
async def test_input_auto_focused():
    async with TutorialApp().run_test(size=(120, 40)) as pilot:
        inp = pilot.app.query_one("#cmd-input")
        assert inp.has_focus


@pytest.mark.asyncio
async def test_can_type_into_input():
    async with TutorialApp().run_test(size=(120, 40)) as pilot:
        await pilot.press("g", "i", "t", " ", "s", "t", "a", "t", "u", "s")
        inp = pilot.app.query_one("#cmd-input")
        assert inp.value == "git status"


@pytest.mark.asyncio
async def test_toggle_sidebar():
    async with TutorialApp().run_test(size=(120, 40)) as pilot:
        app = pilot.app
        main = app.query_one(MainContainer)

        await _defocus_input(pilot)

        assert not app.sidebar_collapsed
        assert "sidebar-collapsed" not in main.classes

        await pilot.press("ctrl+b")
        assert app.sidebar_collapsed
        assert "sidebar-collapsed" in main.classes

        await pilot.press("ctrl+b")
        assert not app.sidebar_collapsed
        assert "sidebar-collapsed" not in main.classes


@pytest.mark.asyncio
async def test_toggle_content():
    async with TutorialApp().run_test(size=(120, 40)) as pilot:
        app = pilot.app
        main = app.query_one(MainContainer)

        await _defocus_input(pilot)

        assert not app.content_collapsed
        assert "content-collapsed" not in main.classes

        await pilot.press("c")
        assert app.content_collapsed
        assert "content-collapsed" in main.classes

        await pilot.press("c")
        assert not app.content_collapsed
        assert "content-collapsed" not in main.classes


@pytest.mark.asyncio
async def test_both_collapsed():
    async with TutorialApp().run_test(size=(120, 40)) as pilot:
        app = pilot.app
        main = app.query_one(MainContainer)

        await _defocus_input(pilot)

        await pilot.press("ctrl+b")
        await pilot.press("c")
        assert app.sidebar_collapsed
        assert app.content_collapsed
        assert "sidebar-collapsed" in main.classes
        assert "content-collapsed" in main.classes


@pytest.mark.asyncio
async def test_help_screen():
    async with TutorialApp().run_test(size=(120, 40)) as pilot:
        await _defocus_input(pilot)
        await pilot.press("?")
        assert isinstance(pilot.app.screen, HelpScreen)
        await pilot.press("escape")
        assert not isinstance(pilot.app.screen, HelpScreen)


@pytest.mark.asyncio
async def test_cheatsheet_screen():
    async with TutorialApp().run_test(size=(120, 40)) as pilot:
        await pilot.press("ctrl+g")
        assert isinstance(pilot.app.screen, CheatSheetScreen)
        await pilot.press("escape")
        assert not isinstance(pilot.app.screen, CheatSheetScreen)


@pytest.mark.asyncio
async def test_search_screen():
    async with TutorialApp().run_test(size=(120, 40)) as pilot:
        await pilot.press("ctrl+f")
        assert isinstance(pilot.app.screen, SearchScreen)
        await pilot.press("escape")
        assert not isinstance(pilot.app.screen, SearchScreen)


@pytest.mark.asyncio
async def test_sidebar_has_phases():
    async with TutorialApp().run_test(size=(120, 40)) as pilot:
        sidebar = pilot.app.query_one(Sidebar)
        nodes = list(sidebar.root.children)
        assert len(nodes) > 0


@pytest.mark.asyncio
async def test_terminal_accepted_initialized():
    async with TutorialApp().run_test(size=(120, 40)) as pilot:
        terminal = pilot.app.query_one(TerminalPanel)
        assert terminal.sandbox is not None
        assert terminal.sandbox.repo_path.exists()
