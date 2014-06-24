#!/usr/bin/python

import nltk, sys, os

while True:
    line = sys.stdin.readline()
    line = nltk.pos_tag(nltk.word_tokenize(line))
    for i in line:
        os.write(1, i[0]+' '+i[1]+' ')
