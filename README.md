# CLI Productivity Tracker

A professional, production-quality Command Line Interface (CLI) application designed to help developers track tasks, manage focus sessions (Pomodoro), build habits, and analyze their daily productivity.

Built with **Python 3.12**, **Typer**, **Rich**, **SQLAlchemy 2.0**, and backed by **PostgreSQL**.

![Dashboard Screenshot Placeholder](#)

## Features

* **User Management**: Support for multiple local user profiles.
* **Task Management**: Create, edit, list, and complete tasks with priority and category filters.
* **Focus Sessions (Pomodoro)**: Interactive terminal countdown timer that logs exactly how much time you spend on specific tasks.
* **Habit Tracking**: Track daily goals and visually monitor your streaks (🔥).
* **Analytics Dashboard**: Aggregates your daily, weekly, and monthly productivity metrics locally using optimized PostgreSQL queries.
* **Exporting**: Dump your data cleanly into CSV or JSON formats.

## Tech Stack & Architecture
* **Language**: Python 3.12
* **CLI Framework**: Typer & Rich
* **Database**: PostgreSQL (via Docker)
* **ORM**: SQLAlchemy 2.0 & Alembic
* **Validation**: Pydantic
* **Architecture**: Clean Architecture (Repositories, Services, Dependency Injection)

---

## 🛠️ Setup & Installation

### Prerequisites
1. **Python 3.12+** installed on your host machine.
2. **Docker** and **Docker Compose** installed (to run the PostgreSQL database).

### 1. Clone & Environment Setup
Clone the repository and create a virtual environment:
```bash
git clone <your-repo-url>
cd cli_project
python -m venv venv

# Activate on Windows:
venv\Scripts\activate
# Activate on Mac/Linux:
# source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure the Database
The project comes with a `.env` file and a `docker-compose.yml` pre-configured for a local database.

Spin up the PostgreSQL database in the background:
```bash
docker-compose up -d
```
*(Note: It maps to port `5433` on your host machine to avoid conflicting with existing native Postgres installations.)*

### 3. Run Migrations
Generate the required database tables using Alembic:
```bash
alembic upgrade head
```

---

## 🚀 Usage Guide

The CLI is invoked via the `src.cli.main` module. 

### User Management
You must create and switch to a user before doing anything else.
```bash
# Create a user (automatically sets them as active)
python -m src.cli.main user create myuser

# Check active profile
python -m src.cli.main user profile

# Switch to another existing user
python -m src.cli.main user switch otheruser
```

### Managing Tasks
```bash
# Create a task
python -m src.cli.main task create "Read System Design Book" --desc "Chapter 1-3" --priority High --category Education

# List all tasks (can be filtered with --priority or --status)
python -m src.cli.main task list

# Complete a task by its ID
python -m src.cli.main task complete 1
```

### Focus Sessions (Pomodoro Timer)
Track time spent on specific tasks!
```bash
# Start an interactive 25-minute Pomodoro timer for Task ID 1
python -m src.cli.main focus timer 1 --minutes 25
```
*(Press `Ctrl+C` to end early—the CLI will gracefully save the exact minutes you spent focusing!)*

### Habit Tracking
```bash
# Add a new habit
python -m src.cli.main habit add "Drink Water"

# List your habits
python -m src.cli.main habit list

# Mark a habit complete for the day to increase your streak
python -m src.cli.main habit mark 1
```

### Analytics Dashboard
View your productivity!
```bash
python -m src.cli.main analytics daily
python -m src.cli.main analytics weekly
python -m src.cli.main analytics monthly
python -m src.cli.main analytics dashboard
```

### Exporting Data
```bash
# Export all your data to JSON
python -m src.cli.main export json --out-dir ./exports

# Export to CSV
python -m src.cli.main export csv --out-dir ./exports
```

---

## 🧪 Testing
The project includes a robust `pytest` suite that uses an isolated in-memory SQLite database. 

To run the tests and view code coverage:
```bash
pytest --cov=src --cov-report=term-missing tests/
```

## 🐳 Docker Deployment
If you wish to containerize the CLI itself, a `Dockerfile` is provided. Build the image:
```bash
docker build -t productivity-tracker .
```
You can then run commands interactively inside the container:
```bash
docker run -it productivity-tracker --help