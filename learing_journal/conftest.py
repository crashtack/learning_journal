import os
import pytest
from pyramid import testing

from passlib.apps import custom_app_context as pwd_context


DB_SETTINGS2 = {'sqlalchemy.url': 'sqlite:///:memory:'}


# app
@pytest.fixture()
def app():
    '''testapp fixture'''
    from learing_journal import main
    app = main({}, **DB_SETTINGS2)
    from webtest import TestApp
    return TestApp(app)


PASSWORD = 'secret password'
ENCRYPTED_PASSWORD = pwd_context.encrypt(PASSWORD)


@pytest.fixture(scope='function')
def auth_env():
    username = 'banksd'
    os.environ['AUTH_USERNAME'] = username
    os.environ['AUTH_PASSWORD'] = ENCRYPTED_PASSWORD

    return username, PASSWORD


@pytest.fixture(scope="function")
def authenticated_app(app_and_csrf_token, auth_env):
    app, token = app_and_csrf_token
    actual_username, actual_password = auth_env
    auth_data = {'username': actual_username,
                 'password': actual_password,
                 'csrf_token': token}
    response = app.post('/login', auth_data, status='3*')

    return app

@pytest.fixture(scope='function')
def app_and_csrf_token(app):
    response = app.get('/login')
    # import pdb; pdb.set_trace()
    input_ = response.html.find('input', attrs={'name': 'csrf_token'})
    token = input_.attrs['value']
    return app, token
