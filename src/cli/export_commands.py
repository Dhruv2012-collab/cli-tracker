import typer
from typing import Optional
from src.cli.utils import console, get_active_user_id, display_error, display_success, UserNotFound
from src.config.dependencies import get_db, get_analytics_service

app = typer.Typer(help="Export user data to various formats")

@app.command()
def csv(out_dir: Optional[str] = typer.Option(None, "--out-dir", "-o", help="Output directory path")):
    """Export tasks and habits to CSV files."""
    try:
        user_id = get_active_user_id()
        service = get_analytics_service()
        with get_db() as db:
            out_path = service.export_data(db, user_id, "csv", out_dir)
            display_success(f"CSV files exported successfully to '{out_path}'")
    except UserNotFound as e:
        display_error(str(e))
    except ValueError as e:
        display_error(str(e))

@app.command()
def json(out_dir: Optional[str] = typer.Option(None, "--out-dir", "-o", help="Output directory path")):
    """Export all user data (tasks, habits, focus sessions) to a JSON file."""
    try:
        user_id = get_active_user_id()
        service = get_analytics_service()
        with get_db() as db:
            out_path = service.export_data(db, user_id, "json", out_dir)
            display_success(f"JSON export completed successfully at '{out_path}'")
    except UserNotFound as e:
        display_error(str(e))
    except ValueError as e:
        display_error(str(e))
