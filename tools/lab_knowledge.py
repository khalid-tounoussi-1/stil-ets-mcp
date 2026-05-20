import json
from pathlib import Path

_DATA = Path(__file__).parent.parent / "data"


def _load(filename: str):
    with open(_DATA / filename) as f:
        return json.load(f)


def get_lab_overview_data() -> dict:
    return _load("lab_info.json")


def get_students_data() -> list[dict]:
    return _load("students.json")


def get_publications_data() -> list[dict]:
    return _load("publications.json")


def get_projects_data() -> list[dict]:
    return _load("projects.json")
