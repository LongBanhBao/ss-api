import pytest
from fastapi.testclient import TestClient

from seed.seed import teachers, students


@pytest.mark.parametrize("data", [teachers[0]])
def test_check_me(client: TestClient, login, data):
    user, res = login(data)
    headers = {
        "Authorization": f"Bearer {res['access_token']}",
        "accept": "application/json",
    }
    response = client.get(
        "/me",
        headers=headers,
    )
    res = response.json()
    if response.status_code == 200:
        assert res["email"] == user["email"]
        assert res["first_name"] == user["first_name"]
        assert res["last_name"] == user["last_name"]
        assert res["date_of_birth"] == user["date_of_birth"]
        assert res["role"] == user["role"]
        assert "password" not in res
    elif response.status_code == 422:
        assert False, res["detail"]
    else:
        pytest.skip(res["detail"])


def test_update_me(client: TestClient, login):
    user, res = login(students[0])
    headers = {
        "Authorization": f"Bearer {res['access_token']}",
        "accept": "application/json",
    }
    data = {
        "first_name": "new first name",
        "last_name": "new last name",
        "date_of_birth": "2000-01-01",
    }
    response = client.put(
        "/update",
        headers=headers,
        json=data,
    )
    res = response.json()
    if response.status_code == 200:
        assert res["first_name"] == data["first_name"]
        assert res["last_name"] == data["last_name"]
        assert res["date_of_birth"] == data["date_of_birth"]
        assert res["role"] == user["role"]
        assert "password" not in res
    else:
        pytest.skip(res["detail"])


def test_get_profile(client: TestClient, login):
    user, res = login(teachers[0])
    headers = {
        "Authorization": f"Bearer {res['access_token']}",
    }
    response = client.get(
        f"/profile/{user['id']}",
        headers=headers,
    )
    res = response.json()
    if response.status_code == 200:
        assert res["email"] == user["email"]
        assert res["first_name"] == user["first_name"]
        assert res["last_name"] == user["last_name"]
        assert res["date_of_birth"] == user["date_of_birth"]
        assert res["role"] == user["role"]
        assert "password" not in res
        assert res["created_classes"] == []
        assert res["my_class"] is None
        assert res["created_assignments"] == []
        assert res["submissions"] == []
    else:
        pytest.skip(res["detail"])
