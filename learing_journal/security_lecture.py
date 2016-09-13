import os
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Everyone, Authenticated
from pyramid.security import Allow
from passlib.apps import custom_app_context as pwd_context
# https://pythonhosted.org/passlib/new_app_quickstart.html
from pyramid.session import SignedCookieSessionFactory


class MyRoot(object):

    def __init__(self, request):
        self.request = request

    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'secret'),
    ]


def includeme(config):
    """security-related configuration"""
    auth_secret = os.environ.get('AUTH_SECRET', 'itsaseekrit')
    authn_policy = AuthTktAuthenticationPolicy(
        secret=auth_secret,
        hashalg='sha512'
    )
    config.set_authentication_policy(authn_policy)
    # add the following new lines of configuration and the new import above.
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    config.set_default_permission('view')
    config.set_root_factory(MyRoot)
    # Bellow added for CSRF
    session_secret = os.environ.get('SESSION_SECRET', '')
    session_factory = SignedCookieSessionFactory(session_secret)
    config.set_session_factory(session_factory)
    config.set_default_csrf_options(require_csrf=True)


def check_credentials(username, password):
    stored_username = os.environ.get('AUTH_USERNAME', '')
    stored_password = os.environ.get('AUTH_PASSWORD', '')
    is_authenticated = False
    if stored_username and stored_password:
        if username == stored_username:
            try:
                is_authenticated = pwd_context.verify(password, stored_password)
            except ValueError:
                # ValueError is rased if teh stored password is not hashed
                pass
    return is_authenticated

# Writen during lecture
def check_credentials2(username, password):
    stored_username = os.environ.get('AUTH_USERNAME')
    stored_password = os.environ.get('AUTH_PASSWORD')
    is_authenticated = False
    if username == stored_username:
        try:
            is_authenticated = pwd_context.verify(password, stored_password)
        except ValueError:
            pass
    return is_authenticated
