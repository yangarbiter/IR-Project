#!/usr/bin/python3

import  nltk,sys, os
while True:
    line = sys.stdin.readline()
    line = nltk.pos_tag(nltk.word_tokenize(line))
    for i in line:
        os.write(1, bytes(i[0]+' '+i[1]+' ', 'utf-8'))
    os.write(1, bytes("\n", 'utf-8'))
    
