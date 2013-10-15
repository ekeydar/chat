import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import options,define

define("port", default=8000, help="run on the given port", type=int)
define('debug', default=True, group='application', help="run in debug mode (with automatic reloading)")

class Application(tornado.web.Application):
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

        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    import pdb
    pdb.set_trace()
    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
