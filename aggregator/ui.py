
import sys
import web

urls = (
    '/$', 'hello',
    '/rss', 'rss'
)
app = web.application(urls, globals())
render = web.template.render('templates/')
rss_builder = None

class hello:        
    def GET(self):
        return render.index()

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

