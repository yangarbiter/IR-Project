#!/usr/bin/python3
import tornado.ioloop, tornado.web, tornado.websocket

STATIC_PATH = './static'

class BaseHandler(tornado.web.RequestHandler):
    pass


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('websocket open')

    def on_message(self, message):
        print(message)

    def on_close(self):
        print("websocket closed")


class MainHandler(BaseHandler):
    def get(self):
        self.render("index.html")
        

application = tornado.web.Application([
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': STATIC_PATH}),
    (r"/ws", WebSocketHandler),
    (r"/", MainHandler),
])


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
