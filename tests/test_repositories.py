from datetime import date, datetime

from sqlalchemy.orm import Session

from src.models.task import TaskStatus
from src.repositories.analytics import analytics_repo
from src.repositories.focus_session import focus_session_repo
from src.repositories.habit import habit_repo
from src.repositories.task import task_repo
from src.repositories.user import user_repo


def test_user_repository(db_session: Session):
    user_in = {"username": "testuser_repo"}
    user = user_repo.create(db_session, user_in)
    assert user.id is not None
    assert user.username == "testuser_repo"

    fetched = user_repo.get_by_username(db_session, "testuser_repo")
    assert fetched is not None
    assert fetched.id == user.id

def test_task_repository(db_session: Session):
    user = user_repo.create(db_session, {"username": "taskuser"})

    task_in = {
        "user_id": user.id,
        "title": "Test Task Repo",
        "status": TaskStatus.PENDING,
        "due_date": date.today()
    }
    task = task_repo.create(db_session, task_in)
    assert task.id is not None

    tasks = task_repo.get_by_user_id(db_session, user.id)
    assert len(tasks) == 1

    task_repo.update(db_session, task, {"status": TaskStatus.COMPLETED})
    completed = task_repo.get_by_status(db_session, user.id, TaskStatus.COMPLETED)
    assert len(completed) == 1

def test_habit_repository(db_session: Session):
    user = user_repo.create(db_session, {"username": "habituser"})

    habit = habit_repo.create(db_session, {"user_id": user.id, "name": "Drink Water"})
    assert habit.id is not None

    fetched = habit_repo.get_by_name(db_session, user.id, "Drink Water")
    assert fetched is not None

def test_focus_session_repository(db_session: Session):
    user = user_repo.create(db_session, {"username": "focususer"})
    task = task_repo.create(db_session, {"user_id": user.id, "title": "Focus Task"})

    fs = focus_session_repo.create(db_session, {
        "task_id": task.id,
        "start_time": datetime.now()
    })

    active = focus_session_repo.get_active_session(db_session, task.id)
    assert active is not None
    assert active.id == fs.id

    focus_session_repo.update(db_session, fs, {"end_time": datetime.now(), "duration": 25})
    active_after = focus_session_repo.get_active_session(db_session, task.id)
    assert active_after is None

def test_analytics_repository(db_session: Session):
    user = user_repo.create(db_session, {"username": "statuser"})
    today = datetime.now().date()

    # Create two tasks, complete one
    task1 = task_repo.create(db_session, {"user_id": user.id, "title": "T1", "category": "Dev"})
    task_repo.update(db_session, task1, {"status": TaskStatus.COMPLETED})
    task2 = task_repo.create(db_session, {"user_id": user.id, "title": "T2"})

    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())

    completed = analytics_repo.get_completed_tasks_in_range(db_session, user.id, start, end)
    assert completed == 1

    pending = analytics_repo.get_pending_tasks_count(db_session, user.id)
    assert pending == 1

    top_cat = analytics_repo.get_most_productive_category(db_session, user.id, start, end)
    assert top_cat == "Dev"
