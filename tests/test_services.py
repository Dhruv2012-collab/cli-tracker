import pytest
from sqlalchemy.orm import Session

from src.cli.utils import ActiveSessionExists
from src.schemas.habit import HabitCreate
from src.schemas.task import TaskCreate, TaskUpdate
from src.schemas.user import UserCreate
from src.services.focus_session import focus_service
from src.services.habit import habit_service
from src.services.task import task_service
from src.services.user import user_service


def test_user_service(db_session: Session):
    u_in = UserCreate(username="svc_user")
    user = user_service.create_user(db_session, u_in)
    assert user.id is not None

    # Duplicate username check
    with pytest.raises(ValueError):
        user_service.create_user(db_session, u_in)

def test_task_service(db_session: Session):
    u = user_service.create_user(db_session, UserCreate(username="task_svc_user"))

    t_in = TaskCreate(user_id=u.id, title="SVC Task")
    task = task_service.create_task(db_session, t_in)

    updated = task_service.update_task(db_session, task.id, TaskUpdate(title="New Title"))
    assert updated.title == "New Title"

    completed = task_service.mark_complete(db_session, task.id)
    assert completed.status.value == "Completed"

def test_focus_service(db_session: Session):
    u = user_service.create_user(db_session, UserCreate(username="focus_svc_user"))
    t = task_service.create_task(db_session, TaskCreate(user_id=u.id, title="Timer Task"))

    session1 = focus_service.start_session(db_session, t.id)
    assert session1.id is not None

    # Prevent overlapping
    with pytest.raises(ActiveSessionExists):
        focus_service.start_session(db_session, t.id)

    stopped = focus_service.stop_session(db_session, t.id)
    assert stopped.duration is not None

def test_habit_service(db_session: Session):
    u = user_service.create_user(db_session, UserCreate(username="habit_svc_user"))

    h = habit_service.create_habit(db_session, HabitCreate(user_id=u.id, name="Run"))
    assert h.streak == 0

    h = habit_service.mark_habit(db_session, h.id)
    assert h.streak == 1

    with pytest.raises(ValueError):
        habit_service.create_habit(db_session, HabitCreate(user_id=u.id, name="Run"))
