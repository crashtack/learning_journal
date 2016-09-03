'''
    These tests where typed out during lecture
    from Cris Ewing September 1, 2016
'''
import os
from pyramid import testing


def test_public_view(app):
    response = app.get('/public')
    assert response.status_code == 200


def test_private_view_Inaccessable(app):
    response = app.get('/private', status='4*')
    # import pdb; pdb.set_trace()
    assert response.status_code == 403


def test_private_view_accaessible_to_authenticated(authenticated_app):
    response = authenticated_app.get('/private', status='2*')
    assert response.status_code == 200


def test_create_view_inaccessable(app):
    response = app.get('/journal/new-entry', status='4*')
    assert response.status_code == 403


def test_create_view_accessible_to_authenticated(authenticated_app):
    response = authenticated_app.get('/journal/new-entry', status='2*')
    assert response.status_code == 200


def test_update_view_inaccessable(app):
    response = app.get('/journal/1/edit-entry', status='4*')
    assert response.status_code == 403


def test_update_view_accessible_to_authenticated(authenticated_app):
    response = authenticated_app.get('/journal/1/edit-entry', status='2*')
    assert response.status_code == 200


def test_detail_view_inaccessable(app):
    response = app.get('/journal/1', status='4*')
    assert response.status_code == 403

# This test is failing now that i am trying to use an in-memory
# sqllite db
def test_detail_view_accessible_to_authenticated(authenticated_app):
    response = authenticated_app.get('/journal/1', status='2*')
    assert response.status_code == 200


def test_auth_username_exists(auth_env):
    assert os.environ.get('AUTH_USERNAME') is not None


def test_auth_username_is_not_empty(auth_env):
    assert os.environ.get('AUTH_USERNAME') != 'billy_goat'


def test_auth_password_exitst(auth_env):
    assert os.environ.get('AUTH_PASSWORD') is not None


def test_auth_password_is_not_empty(auth_env):
    assert os.environ.get('AUTH_PASSWORD') != 'password'


def test_credentials_are_good(auth_env):
    from .security import check_credentials
    actual_uaername, actual_password = auth_env
    assert check_credentials(actual_uaername, actual_password)


def test_bad_username_fail_checks(auth_env):
    from .security import check_credentials
    actual_username, actual_password = auth_env
    fake_username = actual_username + "NOT!!!"
    assert not check_credentials(actual_username, fake_username)


def test_bad_password_fail_checks(auth_env):
    from .security import check_credentials
    actual_uaername, actual_password = auth_env
    fake_password = actual_password + "NOT!!!"
    assert not check_credentials(actual_password, fake_password)


def test_check_jails_if_stored_passeword_is_plaintext(auth_env):
    from .security import check_credentials
    actual_uaername, actual_password = auth_env
    os.environ['AUTH_PASSWORD'] = actual_password
    assert not check_credentials(actual_uaername, actual_password)

# view testing


def test_login_view_get_succeeds(app):
    response = app.get('/login')
    # import pdb: pdb.set_trace() # csrt
    assert response.status_code == 200


# Figuring out CSRF
def test_post_login_view_redirects_on_success(app_and_csrf_token, auth_env):
    app, token = app_and_csrf_token
    actual_username, actual_password = auth_env
    auth_data = {
        'username': actual_username,
        'password': actual_password,
        'csrf_token': token,
    }
    response = app.post('/login', auth_data, status='3*')
    assert response.status_code == 302


def test_post_login_view_has_auth_tkt_cookie(app_and_csrf_token, auth_env):
    app, token = app_and_csrf_token
    actual_username, actual_password = auth_env
    auth_data = {'username': actual_username,
                 'password': actual_password,
                 'csrf_token': token
                 }
    response = app.post('/login', auth_data, status='3*')
    # import pdb; pdb.set_trace()
    for header_name, header_value in response.headerlist:
        if header_name == "Set-Cookie" and header_value.startswith('auth_tkt'):
            break
    else:
        assert False
