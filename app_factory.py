import io
import sys
import cgi
import re
import os

import common

import env_test 
import index_app_page
import sr_redirect
import sr_feed_app
import rss_files_app
import rss_filedownload_app
import app_config

from flask import Flask, after_this_request

app = Flask(__name__)

@app.route('/hello')
def hello():
    return 'hello world'
    
@app.route('/robots.txt')
def hello():
    return  """
User-agent: *
Disallow: /
"""
    
@app.route('/env')
def env_tester():
    return env_test.EnvTest().application()

@app.route('/feed')
def sr_feed_starter():
    return sr_feed_app.SrFeedApp().application()    

@app.route('/episode')
def sr_episode():
    return sr_redirect.SrRedirect().application()

@app.route('/files')
def rss_file_files():
    return rss_files_app.RssFilesApp().application()

@app.route('/filedownload/<path:filepath>')
def rss_filedownload_files(filepath):
    return rss_filedownload_app.RssFileDownloadApp(filepath, app_config.rss_files_paths).application()

@app.route('/')
def index_page():
    return index_app_page.IndexApp().application()

if __name__ == '__main__':

    debug=False
    for a in sys.argv:
       if a.find('debug') >= 0:
           debug=True
     
    # Bind to PORT if defined, otherwise default to 5000.
    penv = os.environ.get('PORT')
    if penv is not None:
        print('PORT env was set to ' + penv)
        port = int(penv)
    else:
        print('PORT env was not set, defaulting to 5000')
        port = 5000
    print('Starting own http server on port ' + str(port) + " debug=" + str(debug))
    app.run(host='0.0.0.0', port=port, debug=debug)

    #else:
    #    print('running app default')
    #    app.run()
