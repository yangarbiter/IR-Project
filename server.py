#!/usr/bin/python3

import tornado.ioloop, tornado.web, tornado.websocket
import json
import subprocess

import google_query
import feedback

STATIC_PATH = './static'
RESULT_PATH = './result'

used_term = {}
make_list_prog = ''
first = True

def getResult():
    with open(RESULT_PATH, "r") as f:
        pass


class BaseHandler(tornado.web.RequestHandler):
    pass


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('websocket open')
        
    def on_message(self, message):
        global make_list_prog
        global first

        if first:
            vocabs = self.get_vocabs()
            first = False

        print(message)
        make_list_prog.stdin.write(bytes(message+'\n', 'utf-8'))
        make_list_prog.stdin.flush()
        vocabs = self.get_vocabs()
        print(vocabs)
        self.send_result(vocabs)

    def on_close(self):
        global make_list_prog
        make_list_prog.terminate()
        #make_list_prog.returncode
        print("websocket closed")

    def get_vocabs(self):
        vocabs = []
        for line in iter(make_list_prog.stdout.readline, b''):
            if line.decode() == '\n':
                break
            vocabs.append(line.decode()[:-1])
        return vocabs

    def send_result(self, vocabs):
        global make_list_prog
        global used_term
        msgs = []
        term_url_pair = []
        for i in vocabs:
            if i in used_term:
                msgs.append(used_term[i])
                vocabs.remove(i)

        queries = google_query.main(vocabs)
        print("query done") 

        for i in range(len(queries)):
            msg = {}
            msg['title'] = queries[i][1][1:-1]
            msg['url'] = queries[i][3]
            msg['content'] = queries[i][2]
            msg['vocab'] = queries[i][0]
            msgs.append(msg)
            
            term_url_pair.append((vocabs[i], msg['url']))

        output = "* "
        ret = feedback.getFeedbackTerms(term_url_pair)
        for p in ret:
            if p[1] in used_term: continue
            output += p[0] + ' '
            output += p[1] + ' '
        #print(output)
        output += '\n'
        make_list_prog.stdin.write(bytes(output, 'utf-8'))
        make_list_prog.stdin.flush()
        self.write_message(json.dumps(msgs))

        for i in msgs:
            used_term[i['vocab']] = i


class FeedbackHandler(BaseHandler):
    def post(self):
        global make_list_prog
        try:
            fb_type = self.get_argument('type')  # accept or remove
            vocab = self.get_argument('vocab')  
            print(fb_type, vocab)

            if fb_type == 'accept':
                output = '&' + vocab + ' True\n'
            else:
                output = '&' + vocab + ' False\n'

            make_list_prog.stdin.write(bytes(output, 'utf-8'))
            make_list_prog.stdin.flush()
            self.write({"success":True})
        except:
            self.write({"success":False})


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
            f.write(speech_info['title'] + '\n')
            f.write(speech_info['speaker'] + '\n')
            f.write(speech_info['description'] + '\n')
            f.write(speech_info['biography'] + '\n')
            f.write('\n')
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
