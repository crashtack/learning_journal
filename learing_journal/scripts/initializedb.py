import os
import sys
import transaction
import datetime
from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)
from ..models import Journal
from ..views.default import ENTRIES


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    settings['sqlalchemy.url'] = os.environ['DATABASE_URL']
    engine = get_engine(settings)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # The below lines populates the database initialy

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        for entry in ENTRIES:
            # intdented like this so the linter stopped complaining
            row = Journal(title=entry['title'], body=entry['body'],
                          date=datetime.datetime.strptime(entry['date'],
                                                          '%B %d, %Y'),
                          date_last_updated=datetime.datetime.strptime(
                          entry['date'], '%B %d, %Y'),
                          id=entry['id'])
            dbsession.add(row)
