import re, collections
import os
import sys
from pymongo import Connection,DESCENDING
from math import *
import datetime

def connect_mongodb():
	connection = Connection('localhost', 27017);
	db = connection.wordnet
	return db

mongodb = connect_mongodb()

def getdatalist():
    text = ''
    for filename in os.listdir("traindata/gutenberg/"):
        if(os.path.splitext(filename)[1]=='.txt'):
            text += file("traindata/gutenberg/"+filename).read()
    return text
def words(text): return re.findall('[a-z]+', text.lower()) 

def train(features):
 #   model = collections.defaultdict(lambda: 1)
	words = mongodb.words
	for f in features:
		print f
		words.update({"lemma":f},{"$inc":{"score":1}})
#        model[f] += 1
	return 1

def trainstart():
	train(words(getdatalist()))

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
	words = mongodb.words
	result = set([])
	for e1 in edits1(word):
		for e2 in edits1(e1):
			result.add(e2)
	if(len(result)>40000):
		return set([])
	result1=  words.find({"lemma":{"$in":list(result)}},{"lemma":1})
	result2= set([])
	for r1 in result1:
		result2.add(r1['lemma'])
	return result2

def known(words): 
	wordscoll = mongodb.words
	result = set([])
	for r1 in wordscoll.find({"lemma":{"$in":list(words)}}):
		result.add(r1['lemma'])
	return set(result)


def correct(word):
	candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
	candidates = list(candidates)
	words = mongodb.words
	result = words.find({"lemma":{"$in":candidates}}).sort("score", DESCENDING)
	for r in result:
		return r['lemma'] 

"""print sys.argv[1]

t1 = datetime.datetime.now()
print correct(sys.argv[1])
t2 = datetime.datetime.now()
td = t2-t1
print(td.seconds,"time taken")"""
"""if(result!=sys.argv[1]):#
	print "Did you mean "+result+" ?" """


