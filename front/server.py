#!/usr/bin/python3
import tornado.ioloop, tornado.web, tornado.websocket

STATIC_PATH = './static'
RESULT_PATH = './result'


def getResult():
    with open(RESULT_PATH, "r") as f:
        pass


class BaseHandler(tornado.web.RequestHandler):
    pass


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        pass
        #print('websocket open')

    def on_message(self, message):
        print(message)
        self.write_message('test')

    def on_close(self):
        pass
        #print("websocket closed")


class InfoHandler(BaseHandler):
    def post(self):
        speech_info = {}
        speech_info['title'] = self.get_argument('title')
        speech_info['speaker'] = self.get_argument('speaker')
        speech_info['description'] = self.get_argument('description')
        speech_info['biography'] = self.get_argument('biography')
        print(speech_info)


class MainHandler(BaseHandler):
    def get(self):
        self.render("index.html")
        

application = tornado.web.Application([
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': STATIC_PATH}),
    (r"/info", InfoHandler),
    (r"/ws", WebSocketHandler),
    (r"/", MainHandler),
])


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
