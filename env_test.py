from app_base import AppBase
import flask

class EnvTest(AppBase):
    def __init__(self):
        AppBase.__init__(self, 'EnvTest')
        
    def application(self):
        # Sorting and stringifying the environment key, value pairs
        self.log(5, "args-type: ", type(flask.request.args))
        
        response_body = 'here are all the ' + str(len(flask.request.args)) + ' args \n'
        for (k, v) in flask.request.args.items():
            self.log(5, k , "= ", v)
            #self.log(5, "d-type= ", type(d), '  k-type=', type(k), '  v-type=', type(v))
            response_body += k + ": " + str(v) + "\n"

        self.log(5, "Environment:\n" + response_body)
       
        return self.make_response(200, response_body, 'text/plain')
