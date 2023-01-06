from app_base import AppBase
from common import combine_http_path

class IndexApp(AppBase):
    def __init__(self):
        AppBase.__init__(self, 'Index')
        
    def application(self):
        return self.generate_help_error(200, '')

    def generate_help_error(self, status_code, error_message_value):
        html_format = """
<html>
<head>
<title>sr_feed start help</title>
<style>
	.demo {{
		border:0px solid #C0C0C0;
		border-collapse:collapse;
		padding:5px;
	}}
	.demo th {{
		border:0px solid #C0C0C0;
		padding:5px;
		background:#F0F0F0;
	}}
	.demo td {{
		border:0px solid #C0C0C0;
		padding:5px;
	}}
</style>
</head>
<body>

{error_message}
<br/>
<br/>
<p><a href="{hello_url}">trivial hello world</a>
<p><a href="{feed_url}">SR feed page</a>
<br/>
<br/>

{error_message}
<br/>
<br/>
<br/>
<br/>
</body>
</html>
        """
        
        hello_url = combine_http_path(self.base_url, 'hello')
        env_url = combine_http_path(self.base_url, 'env')
        feed_url = combine_http_path(self.base_url, 'feed')
        html = html_format.format(
            hello_url = hello_url,
            env_url = env_url,
            feed_url = feed_url,
            error_message=error_message_value
            )
        return self.make_response(status_code, html, 'text/html')
