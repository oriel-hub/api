    ServerAdmin carers-idsapi@aptivate.org

    DocumentRoot /var/www

    ProxyRequests Off
    ProxyPreserveHost Off

    <Proxy *>
    Order deny,allow
    Allow from all
    </Proxy>

    # Django settings

    WSGIScriptAlias / /var/django/idsapi/current/wsgi/wsgi_handler.py
    WSGIApplicationGroup %{GLOBAL}
    WSGIProcessGroup idsapi

    Alias /site_media /var/django/idsapi/current/django/idsapi/media
    <Location "/site_media">
    Require all granted
    SetHandler None
    </Location>

    Alias /static /var/django/idsapi/current/django/idsapi/static
    <Location "/static">
    Require all granted
    SetHandler None
    </Location>

    # Possible values include: debug, info, notice, warn, error, crit,
    # alert, emerg.
    LogLevel warn

    <FilesMatch "^\.(.*)$">
    Require all denied
    </FilesMatch>

    <DirectoryMatch "/\.(.*)">
    Require all denied
    </DirectoryMatch>

    <Directory /var/django/idsapi/current/wsgi>
    <Files wsgi_handler.py>
    Require all granted
    </Files>
    </Directory>

    <Directory /var/django/idsapi/current/django/idsapi/media>
    Require all granted
    </Directory>

    <Directory /var/django/idsapi/current/docs/_build/html>
    Require all granted
    </Directory>
