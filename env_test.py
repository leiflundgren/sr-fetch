from app_base import AppBase
from flask import request

class EnvTest(AppBase):
    def __init__(self):
        AppBase.__init__(self, 'EnvTest')
        
    def application(self):
        # Sorting and stringifying the environment key, value pairs
       response_body = request.query_string

       self.log(5, "response-type: ", type(response_body))
       self.log(5, "Environment:\n" + response_body)
       
       return self.make_response(200, response_body, 'text/plain')

