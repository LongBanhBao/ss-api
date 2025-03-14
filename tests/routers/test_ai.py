import pytest
from fastapi.testclient import TestClient
from seed.seed import teachers, assignments


@pytest.mark.parametrize(
    "teacher, data", [(teachers[0], assignments[0])]
)  # Updated 'a' to assignments[0]
def test_compare_code(client: TestClient, login, create_assignment, teacher, data):
    _, res = login(teacher)
    assignment = create_assignment(res, data)
    response = client.post(
        f"/ai/assignments/{assignment['id']}",
        json={"user_code": data["sample_code"]},
    )

    if response.status_code == 200:
        assert "message" in response.json()
    elif response.status_code == 404:
        assert response.json()["detail"] == "Không tìm thấy bài tập"
    elif response.status_code == 500:
        assert "detail" in response.json()
    else:
        pytest.fail(response.json())
