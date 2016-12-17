from app_base import AppBase
import flask
import os

class EnvTest(AppBase):
    def __init__(self):
        AppBase.__init__(self, 'EnvTest')
        
    def application(self):
        # Sorting and stringifying the environment key, value pairs
        self.log(5, "args-type: ", type(flask.request.args))
        
        response_body = 'here are all the ' + str(len(flask.request.args)) + ' args \n'
        for (k, v) in flask.request.args.items():
            self.log(7, k , "= ", v)
            response_body += k + ": " + str(v) + "\n"

        response_body += "\nEnvironment:\n" 
        for (k, v) in os.environ.items():
            self.log(7, k , " = ", v)
            response_body += k + ": " + str(v) + "\n"
     
        response_body += "\nbase_url: " + self.base_url
        response_body += "\napp_url: " + self.app_url
        response_body += "\nremote_addr: " + self.remote_addr
        

       
        return self.make_response(200, response_body, 'text/plain')
