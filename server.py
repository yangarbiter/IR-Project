#!/usr/bin/python3

import tornado.ioloop, tornado.web, tornado.websocket
import json
import subprocess

import google_query

STATIC_PATH = './static'
RESULT_PATH = './result'

make_list_prog = ''

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
        msgs = []
        global make_list_prog

        print(message)
        vocabs = make_list_prog.communicate(input=bytes(message, 'utf-8'))[0]
        print(vocabs)

        ret = google_query.main()

        for query in ret:
            msg = {}
            msg['title'] = query[1][1:-1]
            msg['url'] = query[3]
            msg['content'] = query[2]
            msg['vocab'] = query[0][:-1]
            msgs.append(msg)

        self.write_message(json.dumps(msgs))

    def on_close(self):
        global make_list_prog
        make_list_prog.terminate()
        #make_list_prog.returncode
        #print("websocket closed")

class FeedbackHandler(BaseHandler):
    def post(self):
        fb_type = self.get_argument('type')  # accept or remove
        vocab = self.get_argument('vocab')  
        print(fb_type, vocab)


class InfoHandler(BaseHandler):
    def post(self):
        POS_TAGGER_PATH = 'scripts/pos_tagger.py'
        CORPUS_PATH = 'make_list/corpus'
        STOPWORD_PATH = 'make_list/stopword'
        INFO_PATH = 'make_list/speech_info'
        PROG_PATH = 'make_list/make_list'
        with open(INFO_PATH, 'w') as f:
            speech_info = {}
            speech_info['title'] = self.get_argument('title')
            speech_info['speaker'] = self.get_argument('speaker')
            speech_info['description'] = self.get_argument('description')
            speech_info['biography'] = self.get_argument('biography')
            f.write('title: ' + speech_info['title'])
            f.write('speaker: ' + speech_info['speaker'])
            f.write('description: ' + speech_info['description'])
            f.write('biography: ' + speech_info['biography'])
        print(speech_info)

        global make_list_prog
        make_list_prog = subprocess.Popen(
                        [PROG_PATH, POS_TAGGER_PATH, CORPUS_PATH, STOPWORD_PATH, INFO_PATH],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE ) 
        



class MainHandler(BaseHandler):
    def get(self):
        self.render("index.html")
        

application = tornado.web.Application([
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': STATIC_PATH}),
    (r"/info", InfoHandler),
    (r"/fb", FeedbackHandler),
    (r"/ws", WebSocketHandler),
    (r"/", MainHandler),
])


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
