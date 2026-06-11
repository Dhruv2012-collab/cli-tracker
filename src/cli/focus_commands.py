import typer
import time
import sys
from typing import Optional
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from datetime import datetime
from src.cli.utils import console, display_error, display_success, get_active_user_id, UserNotFound
from src.config.dependencies import get_db, get_focus_service, get_task_service
from src.schemas.task import TaskUpdate

app = typer.Typer(help="Manage focus sessions")

@app.command()
def start(task_id: int):
    """Start a focus session for a task."""
    try:
        user_id = get_active_user_id()
        task_svc = get_task_service()
        focus_svc = get_focus_service()
        
        with get_db() as db:
            try:
                session = focus_svc.start_session(db, task_id)
                console.print(Panel(
                    f"[bold green]Focus Session Started![/]\nTask ID: {task_id}\nStarted at: {session.start_time.strftime('%H:%M:%S')}",
                    title="Pomodoro",
                    border_style="green"
                ))
            except Exception as e:
                display_error(str(e))
                
    except UserNotFound as e:
        display_error(str(e))

@app.command()
def stop(task_id: int):
    """Stop the active focus session for a task."""
    try:
        user_id = get_active_user_id()
        focus_svc = get_focus_service()
        
        with get_db() as db:
            session = focus_svc.stop_session(db, task_id)
            if session:
                console.print(Panel(
                    f"[bold yellow]Focus Session Stopped[/]\nDuration: {session.duration} minutes",
                    title="Pomodoro",
                    border_style="yellow"
                ))
            else:
                display_error(f"No active session found for task {task_id}.")
                
    except UserNotFound as e:
        display_error(str(e))

@app.command()
def timer(task_id: int, minutes: int = typer.Option(25, "--minutes", "-m", help="Duration of the pomodoro session in minutes")):
    """Start an interactive Pomodoro timer in the terminal."""
    try:
        user_id = get_active_user_id()
        task_svc = get_task_service()
        focus_svc = get_focus_service()
        
        with get_db() as db:
            # Verify task exists
            task = task_svc.update_task(db, task_id, TaskUpdate()) 
            if not task:
                display_error(f"Task ID {task_id} not found.")
                return
            
            try:
                # Start DB Session
                session = focus_svc.start_session(db, task_id)
                console.print(f"[bold cyan]Starting Pomodoro timer for {minutes} minutes...[/] (Press Ctrl+C to stop early)")
                
                total_seconds = minutes * 60
                
                try:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(),
                        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                        TimeRemainingColumn(),
                        console=console,
                    ) as progress:
                        task_id_prog = progress.add_task(f"Focusing on Task {task_id}", total=total_seconds)
                        
                        for _ in range(total_seconds):
                            time.sleep(1)
                            progress.advance(task_id_prog)
                            
                    # Finished naturally
                    stopped_session = focus_svc.stop_session(db, task_id)
                    console.print(Panel(
                        f"[bold green]Pomodoro Complete![/]\nYou stayed focused for {minutes} minutes.",
                        title="Success",
                        border_style="green"
                    ))
                    
                except KeyboardInterrupt:
                    # User cancelled
                    stopped_session = focus_svc.stop_session(db, task_id)
                    actual_minutes = stopped_session.duration if stopped_session else 0
                    console.print()
                    console.print(Panel(
                        f"[bold yellow]Pomodoro Stopped Early[/]\nYou focused for {actual_minutes} minutes.",
                        title="Stopped",
                        border_style="yellow"
                    ))
                    sys.exit(0)

            except Exception as e:
                display_error(str(e))
                
    except UserNotFound as e:
        display_error(str(e))

@app.command()
def current(task_id: int):
    """View current focus session for a task."""
    try:
        user_id = get_active_user_id()
        from src.repositories.focus_session import focus_session_repo
        
        with get_db() as db:
            active = focus_session_repo.get_active_session(db, task_id)
            if active:
                duration = datetime.now() - active.start_time
                minutes = int(duration.total_seconds() / 60)
                console.print(Panel(
                    f"Running for: [bold cyan]{minutes} minutes[/]",
                    title="Current Session",
                    border_style="cyan"
                ))
            else:
                console.print("No active session.")
                
    except UserNotFound as e:
        display_error(str(e))
