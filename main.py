import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import options,define

define("port", default=8000, help="run on the given port", type=int)
define('debug', default=True, group='application', help="run in debug mode (with automatic reloading)")

class ChatApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
            #(r'/', DetailHandler),
            #(r'/cart', CartHandler),
            #(r'/cart/status', StatusHandler)
        ]

        settings = {
            'template_path': 'templates',
            'static_path': 'static'
        }
        
        settings.update(**options.group_dict("application"))

        tornado.web.Application.__init__(self, handlers, **settings)
    
    def print_settings(self):
        for (k,v) in self.settings.iteritems():
            print '%s = %s' % (k,v)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = ChatApplication()
    server = tornado.httpserver.HTTPServer(app)
    print '================================================='
    app.print_settings()
    print 'Listening to port %s' % (options.port)
    print '================================================='
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
