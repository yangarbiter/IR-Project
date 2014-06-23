#!/usr/bin/python

import nltk, sys

while True:
    line = sys.stdin.readline()
    line = nltk.word_tokenize(line)
    print(nltk.pos_tag(line))
