

# default.py

@ veiw.config(route_name='ah-shit', render='string', request_method=('POST', 'PUT'))
def change_things(request)
    # Realy bad shit happens in here



# security.py


# edit-entry.jinja2
# add this
<form action="" method="POST">
    <input type="hidden" name="csrf_token" value="{{ request.session.get_csrf_token() }}" />
    <input type="submit" name="submit" value="Do Dangerous Things" />
</form>
