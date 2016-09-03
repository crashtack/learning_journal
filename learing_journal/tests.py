import pytest
import transaction
import datetime
from pyramid import testing
from pyramid.httpexceptions import HTTPFound

from .models.mymodel import Journal
from .models import get_engine
from .models import get_session_factory
from .models import get_tm_session
from .models.meta import Base


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
        session.add(Journal(title='title: Day 1', body='Thi is a body',
                            date=datetime.datetime.now()))

    def teardown():
        with transaction.manager:
            session.query(Journal).delete()

    request.addfinalizer(teardown)


def test_model_gets_added(new_session):
    assert len(new_session.query(Journal).all()) == 0
    model = Journal(title="test", body='some text')
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(Journal).all()) == 1


def test_model_gets_added_2(new_session):
    """Test the creation of 2 new models in the row."""
    assert len(new_session.query(Journal).all()) == 0
    model = Journal(title="test_day", body="test_body")
    new_session.add(model)
    new_session.flush()
    model = Journal(title="test_day2", body="test_body2")
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(Journal).all()) == 2


# Testing the views
def dummy_http_request(new_session):
    '''a dummy htp request'''
    test_request = testing.DummyRequest()
    test_request.dbsession = new_session
    return test_request


def dummy_http_request_post(title, body, date, new_session):
    '''a dummy http POST request to DB'''
    test_request = testing.DummyRequest()
    test_request.dbsession = new_session
    test_request.method = 'POST'
    test_request.POST['title'] = title
    test_request.POST['body'] = body
    test_request.POST['date'] = date
    return test_request


def test_lists_title(new_session):
    '''tests wether list() pull out correct data from db'''
    from .views.default import home
    new_session.add(Journal(title='test1', body='test2', date=datetime.datetime.now()))
    new_session.flush()
    result = home(dummy_http_request(new_session))
    for entry in result['entries']:
        assert entry.title == 'test1'


def test_lists_body(new_session):
    '''tests wether list() pull out correct data from db'''
    from .views.default import home
    new_session.add(Journal(title='test1', body='test2', date=datetime.datetime.now()))
    new_session.flush()
    result = home(dummy_http_request(new_session))
    for entry in result['entries']:
        assert entry.body == 'test2'


def test_lists_date(new_session):
    '''tests wether list() pull out correct data from db'''
    from .views.default import home
    new_session.add(Journal(title='test1', body='test2',
                    date=datetime.datetime.strptime('August 23, 2016', '%B %d, %Y')))
    new_session.flush()
    result = home(dummy_http_request(new_session))
    for entry in result['entries']:
        assert entry.date.strftime('%B %d, %Y') == 'August 23, 2016'


def test_create_get(new_session):
    """
    Tests whether create() returns  {'title': '', 'body': '', 'error': ''}
    on 'GET' request.
    """
    from .views.default import create
    assert create(dummy_http_request(new_session)) == \
        {'title': '', 'body': '', 'error': ''}


def test_add_new_model(new_session):
    """
    Test if add_new_model() (a helper function) creates a new model.
    Check this using lists().
    """
    from .views.default import home
    home(dummy_http_request_post('a', 'b', 'c', new_session))
    result = home(dummy_http_request(new_session))
    for entry in result['entries']:
        assert entry.title == 'a'


def test_create_error(new_session):
    """
    Test if an error msg shows up on the page
    in case an empty entry on the new_entry page is submitted.
    """
    from .views.default import create
    result = create(dummy_http_request_post('', '', '', new_session))
    assert result['error'] == "You are missing the Title or the Body"


def test_detail_get(new_session):
    """Test if correct details are returned upon calling detail()."""
    from .views.default import detail
    new_session.add(Journal(title='test1', body='test2', date=datetime.datetime.now()))
    new_session.flush()
    request = dummy_http_request(new_session)
    request.matchdict['id'] = 1
    result = detail(request)
    assert result['single_entry'].title == 'test1'


# Testing the templates
# doen't work
from .views.default import ENTRIES
ROUTES = [
    ('/', b'<h2>The list view points here! home.html</h2>'),
    # ('/journal/new-entry', b'<h1>new-entry.jinja2</h1>'),
    ('/journal/' + str(ENTRIES[0]['id']), ENTRIES[0]['title'].encode('utf-8')),
    ('/journal/' + str(ENTRIES[1]['id']), ENTRIES[1]['title'].encode('utf-8')),
    ('/journal/' + str(ENTRIES[2]['id']), ENTRIES[2]['title'].encode('utf-8')),
    ('/journal/' + str(ENTRIES[3]['id']), ENTRIES[3]['title'].encode('utf-8')),
    ('/journal/' + str(ENTRIES[0]['id']), ENTRIES[0]['title'].encode('utf-8')),
    # ('/journal/1/edit-entry', b'Entry ID: 1'),
    # ('/journal/2/edit-entry', b'Entry ID: 2'),
    # ('/journal/3/edit-entry', b'Entry ID: 3'),
    # ('/journal/4/edit-entry', b'Entry ID: 4'),
]




DB_SETTINGS = {'sqlalchemy.url': 'sqlite:///:memory:'}


@pytest.fixture()
def testapp():
    '''testapp fixture'''
    from learing_journal import main
    app = main({}, **DB_SETTINGS)
    from webtest import TestApp
    return TestApp(app)


def test_template_home(testapp):
    '''tests the home '/' route'''
    response = testapp.get('/', status=200)
    # import pdb; pdb.set_trace()
    print('\n\nBody: {}'.format(response.body))
    assert b'<strong>Day 2</strong>' in response.body



@pytest.mark.parametrize('path, content', ROUTES)
def test_rendered_layouts(path, content, authenticated_app):
    '''tests that a particular HTML binary string is in the response body'''
    response = authenticated_app.get(path, status=200)
    # import pdb; pdb.set_trace()
    assert content in response.body

# @pytest.mark.parametrize('path, content', ROUTES)
# def test_rendered_layouts2(path, content, testapp):
#     '''tests that a particular HTML binary string is in the response body'''
#     response = testapp.get(path, status=200)
#     # import pdb; pdb.set_trace()
#     assert content in response.body

#
#
#
#
#
