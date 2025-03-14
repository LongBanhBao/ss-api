from seed.seed import teachers


def test_login(login):
    user, res = login(teachers[0])
    assert "access_token" in res
