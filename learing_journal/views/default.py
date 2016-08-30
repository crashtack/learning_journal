from __future__ import unicode_literals
from pyramid.response import Response
from pyramid.view import view_config
import time
import datetime
from sqlalchemy.exc import DBAPIError
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from ..security import check_credentials
from pyramid.security import NO_PERMISSION_REQUIRED

from ..models import MyModel


ENTRIES = [
    {
        "title": "Day 1",
        "id": 4,
        "date": "August 20, 2016",
        "body": "Today I learned about <strong>Pyramid</strong>."
    },
    {
        "title": "Day 2",
        "id": 2,
        "date": "August 21, 2016",
        "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam. Sed nisi. Nulla quis sem at nibh elementum imperdiet. Duis sagittis ipsum. Praesent mauris. Fusce nec tellus sed augue semper porta. Mauris massa. Vestibulum lacinia arcu eget nulla. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. <b>Lorem ipsum dolor sit amet, consectetur adipiscing elit</b>. Curabitur sodales ligula in libero."
    },
    {
        "title": "Day 3",
        "id": 3,
        "date": "August 28, 2016",
        "body": "Today I figured out how to deploy a postgresql database to Heroku",
    },
    # {
    #     "title": "Day 4",
    #     "id": 4,
    #     "date": "August 23, 2016",
    #     "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam. Sed nisi. Nulla quis sem at nibh elementum imperdiet. Duis sagittis ipsum. Praesent mauris. Fusce nec tellus sed augue semper porta. Mauris massa. Vestibulum lacinia arcu eget nulla. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. <b>Lorem ipsum dolor sit amet, consectetur adipiscing elit</b>. Curabitur sodales ligula in libero."
    # },
    # {
    #     "title": "Day 5",
    #     "id": 5,
    #     "date": "August 24, 2016",
    #     "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam. Sed nisi. Nulla quis sem at nibh elementum imperdiet. Duis sagittis ipsum. Praesent mauris. Fusce nec tellus sed augue semper porta. Mauris massa. Vestibulum lacinia arcu eget nulla. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. <b>Lorem ipsum dolor sit amet, consectetur adipiscing elit</b>. Curabitur sodales ligula in libero."
    # },
]


@view_config(route_name='private', renderer='string', permission='secret')
def private(request):
    return "I am a private view"


@view_config(route_name='login', renderer='templates/login.jinja2', permission=NO_PERMISSION_REQUIRED)
def login(request):
    if request.method == 'POST':
        username = request.params.get('username', '')
        password = request.params.get('password', '')
        if check_credentials(username, password):
            headers = remember(request, username)
            return HTTPFound(location=request.route_url('home'), headers=headers)
    return {}


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)


# TODO: Add a function that handles the POST request.
#       submitting an empty body or title generates error
#       but does not send you back home or to a usefull page
# TODO: add if request.method == 'DELETE':
# TODO: change date string creation to DATETIME
# TODO: add sort by date retreval
# query.orderby(MyModel.date).all()     .all() is the last thing to be done
# from sqlalchemy import desc
# query.order_by(desc(MyModel.date)).all()   # try this
# TODO: added an date_last_updated field

@view_config(route_name='home', renderer='templates/home.jinja2', permission='view')
def home(request):
    # if request.method == 'POST':
    #     print('Title: {}'.format(request.POST['title']))
    #     print('Body: {}'.format(request.POST['body']))
    #     if request.POST['title'] != '' and request.POST['body'] != '':
    #         title = request.POST['title']
    #         body = request.POST['body']
    #         month = time.strftime('%B')
    #         day = time.strftime('%d')
    #         year = time.strftime('%Y')
    #         date = u'{} {}, {}'.format(month, day, year)
    #         new = MyModel(title=title, body=body, date=date)
    #         request.dbsession.add(new)
    #     else:
    #         error_msg = "Can't submit empry entry"
    #         return {'error_msg': error_msg}
    try:
        # import pdb; pdb.set_trace()
        query = request.dbsession.query(MyModel)
        all_entries = query.all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'entries': all_entries, 'poject': 'learning_journal'}


# TODO: update view to take in the title, body, error and display properly
#       if the user entered a body, but no title we want the body to show
#       with a message to input a Title.
@view_config(route_name='create',
             renderer='templates/new-entry.jinja2',
             permission='secret')
def create(request):
    title = body = error = ''
    # if request.method == 'POST':
    #     title = request.params.get('title', '')
    #     body = request.params.get('body', '')
    #     date = datetime.datetime.now()
    #     if not body or not title:
    #         error = 'title and body are both requiered'
    #     else:
    #         new = MyModel(title=title, body=body, date=date)
    #         request.dbsession.add(new)
    #         return HTTPFound(location=request.route_url('home'))

    if request.method == 'POST':
        print('Title: {}'.format(request.POST['title']))
        print('Body: {}'.format(request.POST['body']))
        if request.POST['title'] != '' and request.POST['body'] != '':
            title = request.POST['title']
            body = request.POST['body']
            date = datetime.datetime.now()
            new = MyModel(title=title, body=body, date=date)
            request.dbsession.add(new)
            return HTTPFound(location=request.route_url('home'))
        else:
            error = "Can't submit empry entry"
            return {'error_msg': error_msg}
    return {'title': title, 'body': body, 'error': error}


@view_config(route_name='update', renderer='templates/edit-entry.jinja2', permission='view')
@view_config(route_name='detail', renderer='templates/single-entry.jinja2', permission='secret')
def detail(request):
    try:
        query = request.dbsession.query(MyModel)
        single_entry = query.filter_by(id=request.matchdict['id']).first()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'single_entry': single_entry, 'poject': 'learning_journal'}


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "init_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
