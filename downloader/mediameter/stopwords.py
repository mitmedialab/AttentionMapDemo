#!/usr/bin/python
# -*- coding: utf-8 -*-
# 

################################################################################
# GENERIC STOP WORDS MODULE
# Comprehensive StopWord List from multiple sources
# Dependency: stop-words-english4.txt
# You can add words to the file. Duplicates are removed in getStopWordList process
################################################################################

import nltk
from nltk import Text
from nltk import TextCollection
import math
import re
import time
import string
import sys
import datetime
from datetime import datetime
from nltk.tokenize import RegexpTokenizer
import timeit

def getStopWords():
    sw = StopWords()
    return sw.getStopWords()

class StopWords:

    def __init__(self):
        self.stopwords = self.getStopWordList('stop-words-english4.txt')

################################################################################
# uses file stop-words-english4.txt to extract keywords. Sorts, removes duplicates
################################################################################
    def getStopWordList(self,stopWordListFileName):
        #read the stopwords file and build a list
        stopWords = []
        #you can append stop words like this here
        #stopWords.append('Boston.com')
        #stopWords.append('Your Town')
        #stopWords.append('Boston Globe')
        #sort and remove duplicates
        fp = open(stopWordListFileName, 'r')
        line = fp.readline()
        while line:
            word = line.strip()
            stopWords.append(word.decode('utf-8'))
            line = fp.readline()
        fp.close()
        if stopWords:
            stopWords.sort()
            last = stopWords[-1]
            for i in range(len(stopWords)-2, -1, -1):
                if last == stopWords[i]:
                    del stopWords[i]
                else:
                    last = stopWords[i]
        return stopWords

################################################################################
# return stopwords list
################################################################################
    def getStopWords(self):
        return self.stopwords

################################################################################
# print stopwords list
################################################################################
    def printStopWords(self):
        print self.stopwords
