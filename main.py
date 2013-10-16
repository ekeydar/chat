import json

import tornado.web
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.options
from tornado.options import options,define

define("port", default=8000, help="run on the given port", type=int)
define('debug', default=True, group='application', help="run in debug mode (with automatic reloading)")

class ChatHandler(tornado.web.RequestHandler):
    def build_dict(self):
        if not hasattr(self,'json_dict'):
            self.json_dict = json.loads(self.request.body)
        
    def get_json_val(self,key):
        self.build_dict()
        return self.json_dict[key]
    

class AddMessageHandler(ChatHandler):
    def post(self):
        username = self.get_json_val('username')
        message = self.get_json_val('message')
        print('%s: %s' % (username,message))
        self.application.chatManager.propagate(username,message)
        self.set_status(201)
        
class ChatStreamHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'ChatStreamHandler open'
        self.username = self.get_argument('username')
        self.application.chatManager.propagate_login(self.username,True)
        self.application.chatManager.handlers.append(self)
        
    def on_close(self):
        print 'ChatStreamHandler close'
        self.application.chatManager.remove(self)
        self.application.chatManager.propagate_login(self.username,False)

    def on_message(self, message):
        pass

    def propagate_message(self,username,message):
        self.write_message(dict(username=username,kind='message',message=message))
    def propagate_login(self,username,is_login):
        kind = 'login' if is_login else 'logout'
        self.write_message(dict(username=username,kind=kind))
    
class ChatManager(object):
    def __init__(self):
        self.handlers = []
    def add(self,handler):
        self.handlers.add(handler)
    def remove(self,handler):
        self.handlers.remove(handler)
    def propagate(self,username,message):
        for h in self.handlers:
            h.propagate_message(username,message)

    def propagate_login(self,username,is_login):
        for h in self.handlers:
            h.propagate_login(username,is_login)
    
class ChatApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', tornado.web.RedirectHandler,{'url' : '/static/chat.html'}),
            (r'/api/addMessage', AddMessageHandler),
            (r'/api/chat-stream',ChatStreamHandler),
            #(r'/cart', CartHandler),
            #(r'/cart/status', StatusHandler)
        ]

        settings = {
            'template_path': 'templates',
            'static_path': 'static'
        }
        
        settings.update(**options.group_dict("application"))
        
        self.chatManager = ChatManager()

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
