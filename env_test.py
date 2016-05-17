from app_base import AppBase
import flask

class EnvTest(AppBase):
    def __init__(self):
        AppBase.__init__(self, 'EnvTest')
        
    def application(self):
        # Sorting and stringifying the environment key, value pairs
        self.log(5, "args-type: ", type(flask.request.args))
        
        response_body = ''
        self.log(5, "response : ", str(response_body))
        for (d, k, v) in flask.request.args:
            self.log(5, "d-type= ", type(d), '  k-type=', type(k), '  v-type=', type(v))
            response_body += str(k) + ": " + str(v)

        self.log(5, "Environment:\n" + response_body)
       
        return self.make_response(200, response_body, 'text/plain')


