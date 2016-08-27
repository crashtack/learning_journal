from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import MyModel


ENTRIES = [
    {
        "title": "Day 1",
        "id": 1,
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
        "date": "August 22, 2016",
        "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam. Sed nisi. Nulla quis sem at nibh elementum imperdiet. Duis sagittis ipsum. Praesent mauris. Fusce nec tellus sed augue semper porta. Mauris massa. Vestibulum lacinia arcu eget nulla. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. <b>Lorem ipsum dolor sit amet, consectetur adipiscing elit</b>. Curabitur sodales ligula in libero."
    },
    {
        "title": "Day 4",
        "id": 4,
        "date": "August 23, 2016",
        "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam. Sed nisi. Nulla quis sem at nibh elementum imperdiet. Duis sagittis ipsum. Praesent mauris. Fusce nec tellus sed augue semper porta. Mauris massa. Vestibulum lacinia arcu eget nulla. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. <b>Lorem ipsum dolor sit amet, consectetur adipiscing elit</b>. Curabitur sodales ligula in libero."
    },
]


# @view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
# def my_view(request):
#     try:
#         query = request.dbsession.query(MyModel)
#         one = query.filter(MyModel.name == 'one').first()
#     except DBAPIError:
#         return Response(db_err_msg, content_type='text/plain', status=500)
#     return {'one': one, 'project': 'learing_journal'}


@view_config(route_name='home', renderer='templates/home.jinja2')
def home(request):
    try:
        query = request.dbsession.query(MyModel)
        all_entries = query.all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'entries': all_entries, 'poject': 'learning_journal'}


@view_config(route_name='create', renderer='templates/new-entry.jinja2')
def list_(request):
    try:
        query = request.dbsession.query(MyModel)
        single_entry = query.filter(MyModel.id == int(request.matchdict['id']))
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
