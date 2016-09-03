from pyramid.config import Configurator
import os


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # import pdb; pdb.set_trace()
    if 'sqlalchemy.url' not in settings:
        # import pdb; pdb.set_trace()
        settings["sqlalchemy.url"] = os.environ["DATABASE_URL"]
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.include('.security')
    config.include('.models')
    config.include('.routes')
    config.add_static_view(name='static', path='learing_journal:static')
    config.scan()
    return config.make_wsgi_app()
