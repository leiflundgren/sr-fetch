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

@app.route('/rss')
def sr_feed_starter():
    return sr_feed_app.SrFeedApp().application()    


if __name__ == '__main__':

    debug=False
    for a in sys.argv:
       if a.find('debug') >= 0:
           debug=True
            
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug)
