import os
import pytest
import transaction
import datetime
from pyramid import testing

from .models.mymodel import Journal
from .models import get_engine
from .models.meta import Base
from .models import get_session_factory
from .models import get_tm_session

from passlib.apps import custom_app_context as pwd_context


@pytest.fixture(scope="session")
def sqlengine(request):
    config = testing.setUp(settings={
        'sqlalchemy.url': 'sqlite:///:memory:'
    })
    config.include(".models")
    settings = config.get_settings()
    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    def teardown():
        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(engine)

    request.addfinalizer(teardown)
    return engine


@pytest.fixture(scope="function")
def new_session(sqlengine, request):
    session_factory = get_session_factory(sqlengine)
    session = get_tm_session(session_factory, transaction.manager)

    def teardown():
        transaction.abort()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope="function")
def populated_db(request, sqlengine):
    '''sets up and populates a Data Base for the duration for the test function'''
    session_factory = get_session_factory(sqlengine)
    session = get_tm_session(session_factory, transaction.manager)

    with transaction.manager:
        session.add(Journal(title='title: Day 1', body='This is a body',
                            date=datetime.datetime.now()))
        session.flush()
    def teardown():
        with transaction.manager:
            session.query(Journal).delete()

    request.addfinalizer(teardown)





DB_SETTINGS2 = {'sqlalchemy.url': 'sqlite:///:memory:'}
# DB_SETTINGS2 = {'sqlalchemy.url': 'postgres://banksd:@localhost:5432/learing_journal'}
sqlalchemy.url

# app
@pytest.fixture()
def app(new_session):
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
