from app_base import AppBase

class EnvTest(AppBase):
    def __init__(self, environ, start_response):
        AppBase.__init__(self, 'EnvTest', environ, start_response)
        
    def application(self):
        # Sorting and stringifying the environment key, value pairs
       response_body = ['%s: %s' % (key, value)
                        for key, value in sorted(self.environ.items())]
       response_body = '\n'.join(response_body)

       self.log(5, "response-type: ", type(response_body))
       self.log(5, "Environment:\n" + response_body)

       status = '200 OK'
       response_headers = [('Content-Type', 'text/plain'),
                      ('Content-Length', str(len(response_body)))]
       self.start_response(status, response_headers)

       return [response_body.encode()]

