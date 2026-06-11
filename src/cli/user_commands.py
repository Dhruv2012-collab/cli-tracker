import typer
from rich.table import Table

from src.cli.utils import (
    DuplicateUsername,
    UserNotFound,
    console,
    display_error,
    display_success,
    get_active_user_id,
    set_active_user_id,
)
from src.config.dependencies import get_db, get_user_service
from src.schemas.user import UserCreate

app = typer.Typer(help="Manage users")

@app.command()
def create(username: str):
    """Create a new user and set them as active."""
    service = get_user_service()
    try:
        with get_db() as db:
            try:
                user = service.create_user(db, UserCreate(username=username))
                set_active_user_id(user.id)
                display_success(f"User '{username}' created and set as active!")
            except ValueError as e:
                raise DuplicateUsername(f"Username '{username}' already exists.") from e
    except DuplicateUsername as e:
        display_error(str(e))
    except Exception as e:
        display_error(f"Unexpected error: {str(e)}")

@app.command()
def switch(username: str):
    """Switch to an existing user."""
    service = get_user_service()
    with get_db() as db:
        user = service.get_user(db, username)
        if not user:
            display_error(f"User '{username}' not found.")
            return

        set_active_user_id(user.id)
        display_success(f"Switched to user '{username}'.")

@app.command()
def profile():
    """Show the currently active user profile."""
    try:
        active_id = get_active_user_id()

        with get_db() as db:
            # We need to find user by ID. Service currently only has get by username.
            # Let's query db directly for now, or use repository.
            from src.repositories.user import user_repo
            user = user_repo.get(db, active_id)

            if not user:
                raise UserNotFound("Active user ID no longer exists in database.")

            table = Table(title="User Profile")
            table.add_column("ID", style="cyan")
            table.add_column("Username", style="magenta")
            table.add_column("Active", style="green")

            table.add_row(str(user.id), user.username, str(user.is_active))
            console.print(table)

    except UserNotFound as e:
        display_error(str(e))
