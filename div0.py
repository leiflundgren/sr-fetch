def application(environ, start_response):
    body = "Hello World!\r\n"
    start_response("200 OK", [("Content-Type", "text/plain"), ('x-somthing-else', 'banana')])

  #;  x = 1.0/0.0
    
    return [body]
