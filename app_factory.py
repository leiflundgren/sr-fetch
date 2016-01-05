import io
import cgi
import uwsgi_hello
import re

import env_test 
import sr_redirect
import sr_feed_app
import rss_files_app
import common

known_apps = { 
    'hello_world': uwsgi_hello.UwsgiHello,
    'env_test': env_test.EnvTest,
    'sr_redirect' : sr_redirect.SrRedirect,
    'sr_feed': sr_feed_app.SrFeedApp,
    'rss_files': rss_files_app.RssFilesApp,
}


def application(environ, start_response):
    path = environ['PATH_INFO']

    path_parts = re.findall('[^/\.]+', path)

    log = environ['wsgi.errors']
    print('a am ammy', file=log)

    common.log_handle = log
    common.tracelevel = 5

    for k, v in known_apps.items():
        if k in path_parts:
            common.trace(4, 'Running requested app ' + k)
            return v(environ, start_response).application()

    # Sorting and stringifying the environment key, value pairs
    response_body = 'You wanted to get to "' + cgi.escape(path) + "'\r\nThat is an unknown application\r\n"

    status = '501 Not implemented'
    response_headers = [('Content-Type', 'text/plain'),
                    ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)

    return [response_body]
