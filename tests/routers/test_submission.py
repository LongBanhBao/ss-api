import pytest
from fastapi.testclient import TestClient

from seed.seed import teachers, assignments, students, admins


@pytest.mark.parametrize(
    "user_create, user, data", [(teachers[0], students[0], assignments[0])]
)
def test_create_submission(
    client: TestClient,
    login,
    create_assignment,
    create_submission,
    user_create,
    user,
    data,
):
    _, res = login(user_create)
    assignment = create_assignment(res, data)
    _, res = login(user)

    create_submission(res, assignment, {"code": "print('Hello, World!')"})


@pytest.mark.parametrize(
    "user_create, user, data",
    [
        (teachers[0], teachers[0], assignments[0]),
        (teachers[0], students[0], assignments[0]),
        (teachers[0], admins[0], assignments[1]),
    ],
)
def test_get_submission(
    client: TestClient,
    login,
    create_assignment,
    create_submission,
    user_create,
    user,
    data,
):
    _, res = login(user_create)
    assignment = create_assignment(res, data)
    if user["role"] != "teacher":
        _, res = login(user)
    create_submission(res, assignment, {"code": data["submissions"][0]["code"]})

    headers = {"Authorization": f"Bearer {res['access_token']}"}
    response = client.get(f"/submissions/{assignment['id']}", headers=headers)
    res = response.json()
    if response.status_code == 200:
        assert len(res) == 1
        assert res[0]["code"] == data["submissions"][0]["code"]
        assert "id" in res[0]
        assert "result" in res[0]
        assert "status" in res[0]
    elif response.status_code == 403:
        assert "detail" in res
    elif response.status_code == 404:
        assert "detail" in res
    else:
        assert False, res
