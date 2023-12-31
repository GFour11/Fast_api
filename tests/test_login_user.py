from unittest.mock import MagicMock

from src.database.models import User


def test_create_user(client, user, monkeypatch):
    send_email = MagicMock()
    monkeypatch.setattr('src.repositories.email.send_email', send_email)
    response = client.post(
        "/utils/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json
    assert response.status_code == 201, response.text
    data = response.json()
    res = {}
    assert 'Check your email' == data

def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/utils/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_login_user(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/utils/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, user):
    response = client.post(
        "/utils/login",
        data={"username": user.get('email'), "password": 'password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_login_wrong_email(client, user):
    response = client.post(
        "/utils/login",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"
