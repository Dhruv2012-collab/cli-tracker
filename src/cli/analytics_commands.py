import typer
from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from src.cli.utils import UserNotFound, console, display_error, get_active_user_id
from src.config.dependencies import get_analytics_service, get_db

app = typer.Typer(help="View analytics and reports")

@app.command()
def daily():
    """Generate daily analytics and schedule."""
    try:
        user_id = get_active_user_id()
        service = get_analytics_service()
        with get_db() as db:
            stats = service.get_daily_stats(db, user_id)

            table = Table(title="Daily Analytics", show_header=False)
            table.add_row("Tasks Completed Today", str(stats.tasks_completed))
            table.add_row("Tasks Created Today", str(stats.tasks_created))
            table.add_row("Pending Tasks", str(stats.pending_tasks))
            table.add_row("Total Focus Time (mins)", str(stats.total_focus_minutes))
            table.add_row("Avg Focus Duration (mins)", f"{stats.avg_focus_duration:.1f}")

            habit_txt = ", ".join([f"{h['name']} ({h['streak']} (fire))" for h in stats.current_habit_streaks]) or "None"
            table.add_row("Active Habits", habit_txt)

            console.print(Panel(table, border_style="blue", title="Daily Summary"))
    except UserNotFound as e:
        display_error(str(e))

@app.command()
def weekly():
    """Generate weekly review and stats."""
    try:
        user_id = get_active_user_id()
        service = get_analytics_service()
        with get_db() as db:
            stats = service.get_weekly_stats(db, user_id)

            table = Table(title="Weekly Analytics", show_header=False)
            table.add_row("Tasks Completed", str(stats.tasks_completed))
            table.add_row("Completion %", f"{stats.completion_percentage:.1f}%")
            table.add_row("Missed Deadlines", str(stats.missed_deadlines))
            table.add_row("Most Productive Category", str(stats.most_productive_category or "None"))
            table.add_row("Longest Focus Session (mins)", str(stats.longest_focus_session))
            table.add_row("Total Focus Hours", f"{stats.total_focus_hours:.1f}")
            table.add_row("Avg Daily Completion", f"{stats.avg_daily_completion:.1f}")

            console.print(Panel(table, border_style="green", title="Weekly Summary"))
    except UserNotFound as e:
        display_error(str(e))

@app.command()
def monthly():
    """Generate monthly review and stats."""
    try:
        user_id = get_active_user_id()
        service = get_analytics_service()
        with get_db() as db:
            stats = service.get_monthly_stats(db, user_id)

            table = Table(title="Monthly Analytics", show_header=False)
            table.add_row("Tasks Completed", str(stats.tasks_completed))
            table.add_row("Total Focus Hours", f"{stats.focus_hours:.1f}")
            table.add_row("Top Categories", ", ".join(stats.top_categories) or "None")

            habit_txt = ", ".join([f"{h['name']}: {h['streak']} streak" for h in stats.habit_completion_stats]) or "None"
            table.add_row("Habits", habit_txt)

            console.print(Panel(table, border_style="magenta", title="Monthly Summary"))
    except UserNotFound as e:
        display_error(str(e))

@app.command()
def dashboard():
    """Show comprehensive productivity dashboard."""
    try:
        user_id = get_active_user_id()
        service = get_analytics_service()
        with get_db() as db:
            stats = service.get_dashboard_stats(db, user_id)

            # Build Daily Panel
            d_table = Table(show_header=False, box=None)
            d_table.add_row("Completed", str(stats.daily.tasks_completed))
            d_table.add_row("Pending", str(stats.daily.pending_tasks))
            d_table.add_row("Focus Mins", str(stats.daily.total_focus_minutes))
            d_panel = Panel(d_table, title="Today", border_style="blue")

            # Build Weekly Panel
            w_table = Table(show_header=False, box=None)
            w_table.add_row("Completed", str(stats.weekly.tasks_completed))
            w_table.add_row("Focus Hrs", f"{stats.weekly.total_focus_hours:.1f}")
            w_table.add_row("Best Category", str(stats.weekly.most_productive_category or "None"))
            w_panel = Panel(w_table, title="This Week", border_style="green")

            # Build Habits
            h_table = Table(show_header=False, box=None)
            for h in stats.daily.current_habit_streaks:
                h_table.add_row(h['name'], f"{h['streak']} (fire)")
            h_panel = Panel(h_table, title="Habits", border_style="yellow")

            console.print(Panel(
                Group(d_panel, w_panel, h_panel, f"[bold]Active Goals (Pending Tasks):[/] {stats.active_goals}"),
                title="Productivity Dashboard",
                border_style="cyan"
            ))

    except UserNotFound as e:
        display_error(str(e))
