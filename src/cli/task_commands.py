import typer
from typing import Optional
from datetime import datetime
from rich.table import Table
from src.cli.utils import console, display_error, display_success, get_active_user_id, UserNotFound, TaskNotFound
from src.config.dependencies import get_db, get_task_service
from src.schemas.task import TaskCreate, TaskUpdate
from src.models.task import TaskStatus, TaskPriority

app = typer.Typer(help="Manage tasks")

@app.command()
def create(
    title: str,
    description: Optional[str] = typer.Option(None, "--desc", "-d"),
    priority: TaskPriority = typer.Option(TaskPriority.MEDIUM, "--priority", "-p"),
    category: Optional[str] = typer.Option(None, "--category", "-c"),
    due_date: Optional[str] = typer.Option(None, "--due", "-D", help="YYYY-MM-DD")
):
    """Create a new task."""
    try:
        user_id = get_active_user_id()
        parsed_due = datetime.strptime(due_date, "%Y-%m-%d").date() if due_date else None
        
        task_in = TaskCreate(
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=parsed_due,
            user_id=user_id
        )
        
        service = get_task_service()
        with get_db() as db:
            task = service.create_task(db, task_in)
            display_success(f"Task created with ID {task.id}: '{task.title}'")
    except UserNotFound as e:
        display_error(str(e))
    except ValueError as e:
        display_error(f"Invalid date format: {due_date}. Use YYYY-MM-DD.")

@app.command("list")
def list_tasks(
    status: Optional[TaskStatus] = typer.Option(None, "--status", "-s"),
    priority: Optional[TaskPriority] = typer.Option(None, "--priority", "-p"),
    category: Optional[str] = typer.Option(None, "--category", "-c")
):
    """List tasks with optional filters."""
    try:
        user_id = get_active_user_id()
        service = get_task_service()
        
        with get_db() as db:
            tasks = service.get_user_tasks(db, user_id)
            
            if status:
                tasks = [t for t in tasks if t.status == status]
            if priority:
                tasks = [t for t in tasks if t.priority == priority]
            if category:
                tasks = [t for t in tasks if t.category == category]
            
            if not tasks:
                console.print("No tasks found.")
                return

            table = Table(title="Tasks")
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="magenta")
            table.add_column("Status")
            table.add_column("Priority")
            table.add_column("Category")
            table.add_column("Due Date")

            for t in tasks:
                status_color = "green" if t.status == TaskStatus.COMPLETED else "yellow"
                priority_color = "red" if t.priority == TaskPriority.CRITICAL else "white"
                
                table.add_row(
                    str(t.id),
                    t.title,
                    f"[{status_color}]{t.status.value}[/]",
                    f"[{priority_color}]{t.priority.value}[/]",
                    t.category or "-",
                    str(t.due_date) if t.due_date else "-"
                )
            console.print(table)
            
    except UserNotFound as e:
        display_error(str(e))

@app.command()
def update(
    task_id: int,
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    status: Optional[TaskStatus] = typer.Option(None, "--status", "-s"),
    priority: Optional[TaskPriority] = typer.Option(None, "--priority", "-p")
):
    """Update an existing task."""
    try:
        user_id = get_active_user_id()
        service = get_task_service()
        
        update_data = {}
        if title is not None: update_data["title"] = title
        if status is not None: update_data["status"] = status
        if priority is not None: update_data["priority"] = priority
        
        if not update_data:
            display_error("No fields provided to update.")
            return

        task_in = TaskUpdate(**update_data)
        
        with get_db() as db:
            # We should verify task belongs to user, but for simplicity we rely on task_id
            task = service.update_task(db, task_id, task_in)
            if not task:
                display_error(f"Task {task_id} not found.")
                return
            display_success(f"Task {task_id} updated.")
            
    except UserNotFound as e:
        display_error(str(e))

@app.command()
def delete(task_id: int):
    """Delete a task."""
    try:
        get_active_user_id() # verify logged in
        service = get_task_service()
        
        with get_db() as db:
            success = service.delete_task(db, task_id)
            if success:
                display_success(f"Task {task_id} deleted.")
            else:
                display_error(f"Task {task_id} not found.")
                
    except UserNotFound as e:
        display_error(str(e))

@app.command()
def complete(task_id: int):
    """Mark a task as completed."""
    try:
        get_active_user_id() # verify logged in
        service = get_task_service()
        
        with get_db() as db:
            task = service.mark_complete(db, task_id)
            if task:
                display_success(f"Task {task_id} marked as completed.")
            else:
                display_error(f"Task {task_id} not found.")
                
    except UserNotFound as e:
        display_error(str(e))
