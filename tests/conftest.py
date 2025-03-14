import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from random import randint

from app.main import app
from app.database import get_session
from app.run_code import create_result
from app.models import TestCaseBase


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def create_user(client: TestClient):
    def _create_user(user: dict):
        response = client.post("/register/", json=user)
        res = response.json()
        if response.status_code == 200:
            assert "id" in res
            assert "password" not in res
            res["password"] = user["password"]

            assert res["email"] == user["email"]
            assert res["first_name"] == user["first_name"]
            assert res["last_name"] == user["last_name"]
            assert res["date_of_birth"] == user["date_of_birth"]
            assert res["role"] == user["role"]
            return res
        elif response.status_code == 422:
            assert "detail" in res
            pytest.fail(res["detail"])
        else:
            pytest.fail(res)

    return _create_user


@pytest.fixture()
def login_without_register(client: TestClient):
    def _login_without_register(data: dict):
        response = client.post(
            "/login/",
            data={
                "username": data["email"],
                "password": data["password"],
            },
        )
        res = response.json()
        if response.status_code == 200:
            assert "access_token" in res
            assert "token_type" in res
            assert res["token_type"] == "bearer"
            return res
        elif response.status_code == 422:
            assert "detail" in res
            pytest.fail(res["detail"])
        else:
            pytest.fail(res)

    return _login_without_register


@pytest.fixture()
def login(client: TestClient, create_user):
    def _login(register_data: dict):
        user = create_user(register_data)
        response = client.post(
            "/login/",
            data={
                "username": user["email"],
                "password": user["password"],
            },
        )
        res = response.json()
        if response.status_code == 200:
            assert "access_token" in res
            assert "token_type" in res
            assert res["token_type"] == "bearer"
            return [user, res]
        else:
            pytest.fail(res)

    return _login


def create_assignment_data(data: dict):
    return {
        "title": data["title"],
        "description": data["description"],
        "category": data["category"],
        "sample_code": data["sample_code"],
        "test_cases": data["test_cases"],
    }


@pytest.fixture()
def create_assignment(client: TestClient):
    def _(login_data: dict, assignment: dict):
        headers = {
            "Authorization": f"Bearer {login_data['access_token']}",
            "accept": "application/json",
        }
        response = client.post(
            "/assignments/",
            headers=headers,
            json=create_assignment_data(assignment),
        )
        res = response.json()
        if response.status_code == 200:
            assert "id" in res
            assert res["title"] == assignment["title"]
            assert res["description"] == assignment["description"]
            assert "sample_code" in res
            assert "test_cases" in res
            assert len(res["test_cases"]) == len(assignment["test_cases"])
            index = randint(0, len(res["test_cases"]) - 1)
            test = res["test_cases"][index]
            assert "id" in test
            assert "input" in test
            assert "output" in test
            assert "type" in test
            assert test["input"] == assignment["test_cases"][index]["input"]
            assert test["output"] == assignment["test_cases"][index]["output"]
            assert test["type"] == assignment["test_cases"][index]["type"]
            return res
        elif response.status_code == 422:
            assert "detail" in res
            pytest.fail(res["detail"], "Lỗi xác thực đầu vào")
        elif response.status_code == 403:
            assert "detail" in res
            pytest.fail(res["detail"], "Lỗi quyền truy cập")
        else:
            pytest.fail(res)

    return _


@pytest.fixture()
def create_submission(client: TestClient):
    def _(login_data: dict, assignment_data: dict, data: dict):
        headers = {
            "Authorization": f"Bearer {login_data['access_token']}",
            "accept": "application/json",
        }
        response = client.post(
            f"/submissions/{assignment_data['id']}/",
            headers=headers,
            json=data,
        )
        res = response.json()
        if response.status_code == 200:
            assert "id" in res
            assert "code" in res
            r = create_result(
                res["code"],
                [
                    TestCaseBase(**tc)
                    for tc in assignment_data["test_cases"]
                    if tc["type"] == "hidden"
                ],
            )
            assert res["result"] == r["result"]
            assert res["status"] == r["status"]
            return res
        elif response.status_code == 422:
            assert "detail" in res
            pytest.fail(res["detail"], "Lỗi xác thực đầu vào")
        elif response.status_code == 403:
            assert "detail" in res
            pytest.fail(res["detail"], "Lỗi quyền truy cập")
        else:
            pytest.fail(res)

    return _
