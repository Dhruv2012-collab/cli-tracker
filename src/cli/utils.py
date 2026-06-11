import json
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

CONFIG_FILE = Path.home() / ".tracker_config.json"

class UserNotFound(Exception):
    pass

class TaskNotFound(Exception):
    pass

class ActiveSessionExists(Exception):
    pass

class DuplicateUsername(Exception):
    pass

def get_active_user_id() -> int:
    if not CONFIG_FILE.exists():
        raise UserNotFound("No active user found. Please create or switch to a user.")
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            user_id = data.get("active_user_id")
            if not user_id:
                raise UserNotFound("No active user set.")
            return user_id
    except (json.JSONDecodeError, IOError):
        raise UserNotFound("Error reading user configuration.")

def set_active_user_id(user_id: int):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"active_user_id": user_id}, f)

def display_error(message: str):
    console.print(Panel(message, title="Error", style="bold red"))

def display_success(message: str):
    console.print(Panel(message, title="Success", style="bold green"))
