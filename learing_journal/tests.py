import pytest
import transaction

from pyramid import testing

from .models.mymodel import MyModel
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


def test_model_gets_added(new_session):
    assert len(new_session.query(MyModel).all()) == 0
    model = MyModel(title="test", body='some text')
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(MyModel).all()) == 1


def test_model_gets_added_2(new_session):
    """Test the creation of 2 new models in the row."""
    assert len(new_session.query(MyModel).all()) == 0
    model = MyModel(title="test_day", body="test_body")
    new_session.add(model)
    new_session.flush()
    model = MyModel(title="test_day2", body="test_body2")
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(MyModel).all()) == 2


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
    new_session.add(MyModel(title='test1', body='test2', date='test3'))
    new_session.flush()
    result = home(dummy_http_request(new_session))
    for entry in result['entries']:
        assert entry.title == 'test1'


def test_lists_body(new_session):
    '''tests wether list() pull out correct data from db'''
    from .views.default import home
    new_session.add(MyModel(title='test1', body='test2', date='test3'))
    new_session.flush()
    result = home(dummy_http_request(new_session))
    for entry in result['entries']:
        assert entry.body == 'test2'


def test_lists_date(new_session):
    '''tests wether list() pull out correct data from db'''
    from .views.default import home
    new_session.add(MyModel(title='test1', body='test2', date='test3'))
    new_session.flush()
    result = home(dummy_http_request(new_session))
    for entry in result['entries']:
        assert entry.date == 'test3'


def test_create(new_session):
    """
    Tests whether create() returns  {'poject': 'learning_journal'}
    on 'GET' request.
    """
    from .views.default import create
    assert create(dummy_http_request(new_session)) == \
        {'poject': 'learning_journal'}


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
    from .views.default import home
    result = home(dummy_http_request_post('', '', '', new_session))
    assert result['error_msg'] == "Can't submit empry entry"


def test_detail_get(new_session):
    """Test if correct details are returned upon calling detail()."""
    from .views.default import detail
    new_session.add(MyModel(title='test1', body='test2', date='test3'))
    new_session.flush()
    request = dummy_http_request(new_session)
    request.matchdict['id'] = 1
    result = detail(request)
    assert result['single_entry'].title == 'test1'


#
#
#
#
#
