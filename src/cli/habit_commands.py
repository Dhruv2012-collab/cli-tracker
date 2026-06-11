import typer
from rich.table import Table

from src.cli.utils import UserNotFound, console, display_error, display_success, get_active_user_id
from src.config.dependencies import get_db, get_habit_service
from src.schemas.habit import HabitCreate

app = typer.Typer(help="Manage habits")

@app.command()
def add(name: str):
    """Add a new habit."""
    try:
        user_id = get_active_user_id()
        service = get_habit_service()

        with get_db() as db:
            try:
                habit = service.create_habit(db, HabitCreate(name=name, user_id=user_id))
                display_success(f"Habit '{habit.name}' added with ID {habit.id}")
            except ValueError as e:
                display_error(str(e))

    except UserNotFound as e:
        display_error(str(e))

@app.command()
def mark(habit_id: int):
    """Mark a habit as completed to increment streak."""
    try:
        get_active_user_id()
        service = get_habit_service()

        with get_db() as db:
            habit = service.mark_habit(db, habit_id)
            if habit:
                display_success(f"Habit marked! New streak: {habit.streak} (fire)")
            else:
                display_error(f"Habit {habit_id} not found.")

    except UserNotFound as e:
        display_error(str(e))

@app.command("list")
def list_habits():
    """List all habits and their streaks."""
    try:
        user_id = get_active_user_id()
        service = get_habit_service()

        with get_db() as db:
            habits = service.get_user_habits(db, user_id)

            if not habits:
                console.print("No habits found.")
                return

            table = Table(title="Habit Tracker")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Streak", style="yellow")
            table.add_column("Last Completed")

            for h in habits:
                table.add_row(
                    str(h.id),
                    h.name,
                    f"{h.streak} (fire)",
                    str(h.updated_at.date()) if h.streak > 0 else "-"
                )
            console.print(table)

    except UserNotFound as e:
        display_error(str(e))
