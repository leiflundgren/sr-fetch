import cgi
import uwsgi_hello
import env_test

def application(environ, start_response):
    path = environ['PATH_INFO']

    path_parts = path.split('/')

    if 'hello_world' in path_parts:
        return uwsgi_hello.application(environ, start_response)
    if 'env_test' in path_parts:
        return env_test.application(environ, start_response)

    # Sorting and stringifying the environment key, value pairs
    response_body = 'You wanted to get to ' + cgi.escape(path) + ' That is an unknown application'

    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain'),
                    ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)

    return [response_body]
