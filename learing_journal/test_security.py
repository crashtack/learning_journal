'''
    These tests where typed out during lecture
    from Cris Ewing September 1, 2016
'''
import os
from pyramid import testing


def test_public_view(app):
    '''tests that the public view is public'''
    response = app.get('/public')
    assert response.status_code == 200


def test_private_view_Inaccessable(app):
    '''tests that the priveate view is private'''
    response = app.get('/private', status='4*')
    # import pdb; pdb.set_trace()
    assert response.status_code == 403


def test_private_view_accaessible_to_authenticated(authenticated_app):
    '''test that the private view is accessable to authenticated'''
    response = authenticated_app.get('/private', status='2*')
    assert response.status_code == 200


def test_create_view_inaccessable(app):
    '''test the create view is inaccessable to nonauthorized'''
    response = app.get('/journal/new-entry', status='4*')
    assert response.status_code == 403


def test_create_view_accessible_to_authenticated(authenticated_app):
    '''ttest that the create view is accessable to authenticated user'''
    response = authenticated_app.get('/journal/new-entry', status='2*')
    assert response.status_code == 200


def test_update_view_inaccessable(app):
    '''test that the update view is inaccesable to unauthorized user'''
    response = app.get('/journal/1/edit-entry', status='4*')
    assert response.status_code == 403


def test_update_view_accessible_to_authenticated(authenticated_app):
    '''test the update view is accessable to authenticated user'''
    response = authenticated_app.get('/journal/1/edit-entry', status='2*')
    assert response.status_code == 200


def test_detail_view_inaccessable(app):
    '''test the detail view is inaccessable to unauthorized'''
    response = app.get('/journal/1', status='4*')
    assert response.status_code == 403


def test_detail_view_accessible_to_authenticated(authenticated_app,
                                                 populated_db):
    '''test teh detail view is accessable to authenticated'''
    response = authenticated_app.get('/journal/1', status='2*')
    assert response.status_code == 200


def test_auth_username_exists(auth_env):
    '''test that AUTH_USERNAME exists'''
    assert os.environ.get('AUTH_USERNAME') is not None


def test_auth_username_is_not_empty(auth_env):
    '''test AUTH_USERNAME is not empty'''
    assert os.environ.get('AUTH_USERNAME') != 'billy_goat'


def test_auth_password_exitst(auth_env):
    '''test AUTH_PASSWORD exists'''
    assert os.environ.get('AUTH_PASSWORD') is not None


def test_auth_password_is_not_empty(auth_env):
    '''tests AUTH_PASSWORD is not empty'''
    assert os.environ.get('AUTH_PASSWORD') != 'password'


def test_credentials_are_good(auth_env):
    '''tests credentials are goog'''
    from .security import check_credentials
    actual_uaername, actual_password = auth_env
    assert check_credentials(actual_uaername, actual_password)


def test_bad_username_fail_checks(auth_env):
    '''tests bad username fails credential check'''
    from .security import check_credentials
    actual_username, actual_password = auth_env
    fake_username = actual_username + "NOT!!!"
    assert not check_credentials(actual_username, fake_username)


def test_bad_password_fail_checks(auth_env):
    '''test bad password fails'''
    from .security import check_credentials
    actual_uaername, actual_password = auth_env
    fake_password = actual_password + "NOT!!!"
    assert not check_credentials(actual_password, fake_password)


def test_check_fails_if_stored_passeword_is_plaintext(auth_env):
    '''test if password is plain text'''
    from .security import check_credentials
    actual_uaername, actual_password = auth_env
    os.environ['AUTH_PASSWORD'] = actual_password
    assert not check_credentials(actual_uaername, actual_password)


# view testing
def test_login_view_get_succeeds(app):
    '''test login view is successfull'''
    response = app.get('/login')
    # import pdb: pdb.set_trace() # csrt
    assert response.status_code == 200


def test_post_login_view_redirects_on_success(app_and_csrf_token, auth_env):
    '''tests login view POST redirects succsssfully'''
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
    '''tests login view POST method requires csrf_token'''
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
