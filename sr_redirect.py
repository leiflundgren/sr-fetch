class sr_redirect(object):
    """A class that takes a request un query-string, finds the appropriate SR episode and redirects to the download URL"""

    def application(environ, start_response):
        pass
    

def application(environ, start_response):
    return sr_redirect().application(environ, start_response)
