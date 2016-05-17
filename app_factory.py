import io
import sys
import cgi
import re
import os

import common

import uwsgi_hello
import env_test 
import sr_redirect
import sr_feed_app
import rss_files_app

from flask import Flask, after_this_request

app = Flask(__name__)



known_apps = { 
    'hello_world': uwsgi_hello.UwsgiHello,
    'env_test': env_test.EnvTest,
    'sr_redirect' : sr_redirect.SrRedirect,
    'sr_feed': sr_feed_app.SrFeedApp,
    'rss_files': rss_files_app.RssFilesApp,
}

@app.route('/hello')
def hello():
    return 'hello world'
    
@app.route('/env')
def env_tester():
    return env_test.EnvTest().application()
    

def application(environ, start_response):
    path = environ['PATH_INFO']

    path_parts = re.findall('[^/\.]+', path)

    print('this is the beginning', file=sys.stderr)
    print('environ[wsgi.errors] is ' + str(type(environ['wsgi.errors'])) + ': ' + str(environ['wsgi.errors']), file=sys.stderr)

    log = environ['wsgi.errors']
    print('a am ammy', file=log)
    log=sys.stderr

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

    return [response_body.encode()]


if __name__ == '__main__':

    debug=False
    for a in sys.argv:
       if a.find('debug') >= 0:
           debug=True
            
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug)
