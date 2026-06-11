import typer
from rich.console import Console

from src.cli.analytics_commands import app as analytics_app
from src.cli.export_commands import app as export_app
from src.cli.focus_commands import app as focus_app
from src.cli.habit_commands import app as habit_app
from src.cli.task_commands import app as task_app
from src.cli.user_commands import app as user_app

console = Console()

app = typer.Typer(
    name="tracker",
    help="CLI Productivity Tracker",
    no_args_is_help=True
)

app.add_typer(user_app, name="user")
app.add_typer(task_app, name="task")
app.add_typer(focus_app, name="focus")
app.add_typer(habit_app, name="habit")
app.add_typer(analytics_app, name="analytics")
app.add_typer(export_app, name="export")

if __name__ == "__main__":
    app()
