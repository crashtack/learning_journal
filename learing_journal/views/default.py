from __future__ import unicode_literals
from pyramid.response import Response
from pyramid.view import view_config
import time
import datetime
from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from ..security import check_credentials
from pyramid.security import NO_PERMISSION_REQUIRED

from ..models import Journal


ENTRIES = [
    {
        "title": "Day 1",
        "id": 20,
        "date": "August 20, 2016",
        "body": "Today I learned about <strong>Pyramid</strong>."
    },
    {
        "title": "Day 2",
        "id": 21,
        "date": "August 21, 2016",
        "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam. Sed nisi. Nulla quis sem at nibh elementum imperdiet. Duis sagittis ipsum. Praesent mauris. Fusce nec tellus sed augue semper porta. Mauris massa. Vestibulum lacinia arcu eget nulla. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. <b>Lorem ipsum dolor sit amet, consectetur adipiscing elit</b>. Curabitur sodales ligula in libero."
    },
    {
        "title": "Day 3",
        "id": 22,
        "date": "August 28, 2016",
        "body": "Today I figured out how to deploy a postgresql database to Heroku",
    },
    {
        "title": "Day 4: Yum Bacon",
        "id": 23,
        "date": "August 23, 2017",
        "body": "Anim cupidatat ham hamburger short ribs. Enim do hamburger, tenderloin turducken incididunt shankle aliquip reprehenderit turkey capicola. Minim deserunt swine, eiusmod consequat veniam commodo jerky andouille reprehenderit kevin pariatur adipisicing quis. Aute salami kevin sint chicken ut.",
    },
]


@view_config(route_name='private', renderer='string', permission='secret')
def private(request):
    return "I am a private view"


@view_config(route_name='public', renderer='string')
def public(request):
    return "I am a private view"


# TODO: if there is a login failure give a message, and stay here
@view_config(route_name='login', renderer='templates/login.jinja2')
def login(request):
    if request.method == 'POST':
        username = request.params.get('username', '')
        password = request.params.get('password', '')
        if check_credentials(username, password):
            headers = remember(request, username)
            return HTTPFound(location=request.route_url('home'),
                             headers=headers)
        else:
            return {'error': "Username or Password Not Recognized"}
    return {'error': ''}


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)


# TODO: test the routes
# TODO: add if request.method == 'DELETE':
@view_config(route_name='home', renderer='templates/home.jinja2',
             permission='view')
def home(request):
    try:
        query = request.dbsession.query(Journal)
        all_entries = query.order_by(desc(Journal.date)).all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'entries': all_entries}


@view_config(route_name='create',
             renderer='templates/new-entry.jinja2',
             permission='secret')
def create(request):
    '''handles the POST request to create a new entry'''
    title = body = error = ''

    if request.method == 'POST':
        title = request.POST['title']
        body = request.POST['body']
        print('\nTitle: {}'.format(title))
        print('Body: {}\n'.format(body))

        if title != '' and body != '':
            date = datetime.datetime.now()
            date_last_updated = datetime.datetime.now()
            new = Journal(title=title, body=body, date=date,
                          date_last_updated=date_last_updated)
            request.dbsession.add(new)
            return HTTPFound(location=request.route_url('home'))
        else:
            error = "You are missing the Title or the Body"
            return {'title': title, 'body': body, 'error': error}
    return {'title': title, 'body': body, 'error': error}


@view_config(route_name='update', renderer='templates/edit-entry.jinja2',
             permission='secret')
@view_config(route_name='detail', renderer='templates/single-entry.jinja2',
             permission='secret')
def detail(request):
    '''handles the GET and POST method for edit-entry and single-entry'''
    try:
        query = request.dbsession.query(Journal)
        single_entry = query.filter_by(id=request.matchdict['id']).first()
        if request.method == 'POST':
            single_entry.title = request.POST['title']
            single_entry.body = request.POST['body']
            return HTTPFound(location=request.route_url('home'))
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'single_entry': single_entry}


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
