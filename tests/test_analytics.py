import csv
import json
import os

from sqlalchemy.orm import Session

from src.schemas.task import TaskCreate
from src.schemas.user import UserCreate
from src.services.analytics import analytics_service
from src.services.task import task_service
from src.services.user import user_service


def test_analytics_service(db_session: Session):
    u = user_service.create_user(db_session, UserCreate(username="analytics_user"))

    t1 = task_service.create_task(db_session, TaskCreate(user_id=u.id, title="A1", category="Dev"))
    t2 = task_service.create_task(db_session, TaskCreate(user_id=u.id, title="A2", category="Dev"))

    task_service.mark_complete(db_session, t1.id)

    daily = analytics_service.get_daily_stats(db_session, u.id)
    assert daily.tasks_completed == 1
    assert daily.tasks_created == 2
    assert daily.pending_tasks == 1

    weekly = analytics_service.get_weekly_stats(db_session, u.id)
    assert weekly.tasks_completed == 1
    assert weekly.most_productive_category == "Dev"

def test_export_data(db_session: Session, tmp_path):
    u = user_service.create_user(db_session, UserCreate(username="export_user"))
    task_service.create_task(db_session, TaskCreate(user_id=u.id, title="ExportTask"))

    out_dir = str(tmp_path)

    # JSON Export
    json_path = analytics_service.export_data(db_session, u.id, "json", out_dir)
    assert os.path.exists(json_path)
    with open(json_path, "r") as f:
        data = json.load(f)
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "ExportTask"

    # CSV Export
    csv_dir = analytics_service.export_data(db_session, u.id, "csv", out_dir)
    assert os.path.exists(os.path.join(csv_dir, "tasks.csv"))

    with open(os.path.join(csv_dir, "tasks.csv"), "r") as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == 2 # header + 1 row
        assert rows[1][1] == "ExportTask"
