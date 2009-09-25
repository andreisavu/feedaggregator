
import sys
import web

urls = (
    '/$', 'hello',
    '/rss', 'rss'
)
app = web.application(urls, globals())
rss_builder = None

class hello:        
    def GET(self):
        return """
<html>
<head></head>
<body>
    <h2>Hbase powered feed aggregator</h2>
    <a href="/rss">Global aggregated feed</a> (only the latest 24 hours)<br />
    <br />
    <form action="/rss" method="GET">
        <legend>Customize</legend>
        <label>Category:</label>
        <input  type="text" name="c" />
        <label>Hours:</label>
        <input type="text" name="h" />
        <button type="submit">Do the magic</button>
    </form>
</body>
</html>
"""

class rss:
    def GET(self):
        web.header("Content-Type","application/rss+xml")
        input = web.input(c='', h=None)
        return rss_builder(input.h, input.c)
       

def start(builder):
    """
    Start the webui and use the given RSS builder for answering queries
    """
    global rss_builder
    rss_builder, sys.argv = builder, []
    app.run()

