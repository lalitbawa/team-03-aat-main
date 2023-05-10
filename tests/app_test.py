from AATApp import app
from pathlib import Path


def test_index():
    tester = app.test_client()
    response = tester.get("/", content_type="html/text")

    assert response.status_code == 200


def test_database():
    # path of containing folder for whole project
    root = Path(__file__).resolve().parent.parent
    app_path = root / "AATApp"  # path of "AATApp"
    db = app_path / "app.db"  # path of "app.db" within AATApp folder
    assert db.is_file()
