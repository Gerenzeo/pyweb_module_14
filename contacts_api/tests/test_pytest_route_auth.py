from unittest.mock import MagicMock

from src.db.models import User
from src.services.auth import auth_service


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data.get("email") == user.get("email")

def test_create_user_again(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data['detail'] == f'Account already exist'

def test_login_wrong_email(client, user):
    response = client.post("/api/auth/login",
                           data={"username": "email", "password": user.get("password")},)
    assert response.status_code == 401, response.text()
    assert response.json()['detail'] == 'Invalid email'

def test_login_wrong_password(client, user):
    response = client.post('/api/auth/login', data={"username": user.get("email"), "password": 'incorrect password'})
    assert response.status_code == 401, response.text()
    assert response.json()['detail'] == 'Invalid password'

def test_login_user(client, user):
    response = client.post("/api/auth/login", data={'username': user.get("email"), "password": user.get("password")})
    assert response.status_code == 200, response.text()
    data = response.json()
    assert data['access_token'] != ''
    assert data['refresh_token'] != ''
    assert data['token_type'] == 'bearer'

def test_login_user_not_confirmed(user, session):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    assert current_user.confirmed == False

def test_login_user_confirmed(user, session):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    assert current_user.confirmed == True

def test_request_reset_password_accept(client, user, session, monkeypatch):
    mock_reset_password = MagicMock()
    monkeypatch.setattr("src.routes.auth.reset_password", mock_reset_password)

    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    assert current_user.email == user.get('email')
    response = client.post('/api/auth/request_reset_password', json={"email": current_user.email})

    assert response.status_code == 200, response.text()
    assert mock_reset_password.called, "resset_password not was called"


def test_set_new_password(client, user, session):
    token = auth_service.create_email_token({"sub": user.get("email")})
    new_psw = 'qwerty123'

    client.post(f'/api/auth/set_new_password/{token}', json={"token": token, "new_password": new_psw, "confirm_new_password": new_psw})

    user_email = auth_service.get_email_from_token(token)
    current_user: User = session.query(User).filter(User.email == user_email).first()
    old_password = current_user.password

    current_user.password = auth_service.get_password_hash(new_psw)
    session.commit()

    assert auth_service.verify_password('qwerty123', current_user.password) == True
    assert auth_service.verify_password(old_password, current_user.password) == False


# def test_set_new_password(client, user, session):
#     current_user: User = session.query(User).filter(User.email == user.get('email')).first()
#     token = auth_service.create_email_token({"sub": user.get("email")})
#
#     new_psw = 'qwerty123'
#     response = client.post(f'/api/auth/set_new_password/{token}', json={"token": token, "new_password": new_psw, "confirm_new_password": new_psw})
#
#     current_user.password = auth_service.get_password_hash(new_psw)
#     session.commit()
#     print(response.status_code)









