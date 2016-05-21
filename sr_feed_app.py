import cgi
from app_base import AppBase
import sr_feed
import flask

class SrFeedApp(AppBase):
    """A class that takes a request un query-string, finds the appropriate SR episode and redirects to the download URL"""
    def __init__(self):
        AppBase.__init__(self, 'SrFeed')
        
    def generate_help_error(self, status_code, error_message):
        html = """
<html>
<head>
<title>sr_feed_app help</title>
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
This is the SR feed generator<br />
<br/>
<br/>

<b>{error_message}</b>
<br/>
<br/>

<table class="demo">
	<thead>
	<tr>
		<th>option</th>
		<th>default<br></th>
		<th>desc<br></th>
	</tr>
	</thead>
	<tbody>
	<tr>
		<td>tracelevel</td>
		<td>3</td>
		<td>How detailed the serverlogs will be</td>
	</tr>
	<tr>
		<td>progrtamid</td>
		<td>required</td>
		<td>Which program to get info for. Look in the page-URL for Svergies Radios program to get the ID.</td>
	</tr>
	<tr>
		<td>format</td>
		<td>rss</td>
		<td>Which format to genereate the feed in. <tt>rss</tt> and <tt>atom</tt> is supported.</td>
	</tr>
	<tr>
		<td>source</td>
		<td>feed</td>
		<td>Source to find which episodes exists. Default is <tt>feed</tt> from http://api.sr.se/api/rss/program/1234. 
        Alternative is <tt>html</tt> from http://sverigesradio.se/sida/avsnitt?programid=1234 </td>
	</tr>
	<tr>
		<td>proxy_data</td>
		<td>false</td>
		<td>When requesting a file, proxy the data rather than making a redirect. Currently not implemented.</td>
	</tr>
	<tbody>
</table>

<br/>
Sample test URL: <a href="{app_url}?tracelevel=5&programid=4429&format=rss">{app_url}?tracelevel=5&programid=4429&format=rss</a>
<br/>
<br/>
</body>
</html>
        """.format(
            app_url=self.app_url,
            error_message=error_message
            )
        return self.make_response(status_code, html)

    def application(self):

        programid = self.qs_get('programid') 
        if not programid:
            return self.generate_help_error(500, 'parameter programid is required!')
            
        if not programid.isdigit():
            return self.generate_help_error(500, 'parameter programid must be numbers!')

        proxy_data = self.qs_get('proxy_data', 'False').lower() == 'true'
        format = self.qs_get('format', 'rss') 

        source = self.qs_get('source', 'feed')

        if source == 'feed':
            prog_url = 'http://api.sr.se/api/rss/program/' + str(programid)
        elif source == 'html':
            prog_url = 'http://sverigesradio.se/sida/avsnitt?programid=' + str(programid)
        else:
            return self.generate_help_error(500, 'unsupported source. Must be feed/html!')            

        self.log(4, 'Attempt to find prog=' + str(programid)  + ', proxy_data = ' + str(proxy_data) + ' from ' + prog_url)
        feeder = sr_feed.SrFeed(self.base_url, prog_url, str(programid), self.tracelevel, format, proxy_data)
        feed_data = feeder.get_feed().encode()
        self.log(9, 'feed_data is ' + str(type(feed_data)) + " len=" + str(len(feed_data)))
        # self.log(4, 'Result is ', feed_data)
        return self.make_response(200, feed_data, feeder.content_type)


     
