import pytest
from fastapi.testclient import TestClient
from random import randint

from seed.seed import teachers, students, assignments, admins


@pytest.mark.parametrize("user, data", [(teachers[0], assignments[0])])
def test_create_assignment(client: TestClient, login, create_assignment, user, data):
    _, res = login(user)
    assignment = create_assignment(res, data)
    assert "id" in assignment
    assert "sample_code" in assignment
    assert "test_cases" in assignment
    assert len(assignment["test_cases"]) == len(data["test_cases"])
    for a in assignment["test_cases"]:
        assert "id" in a
        assert a["input"] in [tc["input"] for tc in data["test_cases"]]
        assert a["output"] in [tc["output"] for tc in data["test_cases"]]
        assert a["type"] in [tc["type"] for tc in data["test_cases"]]
    assert "submissions" not in assignment


@pytest.mark.parametrize("user, data", [(teachers[0], assignments)])
def test_get_assignments(
    client: TestClient, login, create_assignment, user, data: list
):
    _, res = login(user)
    assignments_created = []
    for d in data:
        assignment = create_assignment(res, d)
        assignments_created.append(assignment)
    res = client.get("/assignments")
    assert res.status_code == 200
    assignments = res.json()
    assert len(assignments) == len(assignments_created)


@pytest.mark.parametrize(
    "user_create, user, data",
    [
        (teachers[0], teachers[0], assignments[0]),
        (teachers[0], students[0], assignments[0]),
        (teachers[0], admins[0], assignments[0]),
    ],
)
def test_get_one_assignment(
    client: TestClient,
    login,
    create_assignment,
    create_submission,
    user_create,
    user: dict,
    data,
):
    _, res = login(user_create)
    assignment = create_assignment(res, data)
    if user["role"] != "teacher":
        _, res = login(user)
    for sub in data["submissions"]:
        create_submission(res, assignment, {"code": sub["code"]})
    headers = {"Authorization": f"Bearer {res['access_token']}"}
    res = client.get(f"/assignments/{assignment['id']}", headers=headers)
    assignment_res = res.json()

    if res.status_code == 404:
        assert assignment_res["detail"] == "Bài tập không tồn tại"
    elif res.status_code == 200 and user["role"] == "admin":
        assert assignment_res["id"] == assignment["id"]
        assert assignment_res["title"] == assignment["title"]
        assert assignment_res["description"] == assignment["description"]
        assert assignment_res["sample_code"] == assignment["sample_code"]
        assert len(assignment_res["test_cases"]) == len(assignment["test_cases"])
        assert len(assignment_res["submissions"]) == len(data["submissions"])
        assert len(assignment_res["saved_codes"]) == 0
    elif res.status_code == 200 and user["role"] == "teacher":
        assert assignment_res["id"] == assignment["id"]
        assert assignment_res["title"] == assignment["title"]
        assert assignment_res["description"] == assignment["description"]
        assert assignment_res["sample_code"] == assignment["sample_code"] or None
        assert len(assignment_res["test_cases"]) == len(assignment["test_cases"])
        assert len(assignment_res["submissions"]) == len(data["submissions"])
        assert len(assignment_res["saved_codes"]) == 0
    elif res.status_code == 200 and user["role"] == "student":
        assert assignment_res["id"] == assignment["id"]
        assert assignment_res["title"] == assignment["title"]
        assert assignment_res["description"] == assignment["description"]
        assert assignment_res["sample_code"] is None
        assert len(assignment_res["test_cases"]) == len(
            [tc for tc in assignment["test_cases"] if tc["type"] != "hidden"]
        )
        assert len(assignment_res["submissions"]) == len(data["submissions"])
        assert len(assignment_res["saved_codes"]) == 0
    else:
        assert False, assignment_res


@pytest.mark.parametrize(
    "user_create, user, data", [(teachers[0], teachers[0], assignments[0])]
)
def test_delete_assignment(
    client: TestClient, login, create_assignment, user_create, user, data
):
    _, res = login(user_create)
    assignment = create_assignment(res, data)
    if user_create["email"] == user["email"]:
        headers = {"Authorization": f"Bearer {res['access_token']}"}
    else:
        _, res = login(user)
        headers = {"Authorization": f"Bearer {res['access_token']}"}
    res = client.delete(f"/assignments/{assignment['id']}", headers=headers)
    if res.status_code == 404:
        assert res.json()["detail"] == "Bài tập không tồn tại"
    elif res.status_code == 200:
        assert "id" in res.json()
    else:
        assert False, res.json()
