#import MySQLdb
from flask import Flask,render_template, url_for,request,g
from spellcheck import correct
from pymongo import Connection


import datetime

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

# create the little application object
app = Flask(__name__)
app.config.from_object(__name__)

# connect to the database
"""def connect_mysql():
	conn = MySQLdb.connect (host = "localhost",
                           user = "root",
                           passwd = "abcd1234",
                           db = "wordnet")
	return conn"""

def connect_mongodb():
	connection = Connection('localhost', 27017);
	db = connection.wordnet
	return db

@app.before_request
def before_request():
	#g.mysql_db = connect_mysql()
	#g.mysql_cursor = g.mysql_db.cursor(MySQLdb.cursors.DictCursor)	
	g.mongodb = connect_mongodb()

@app.route('/')
def index():
    return render_template('search.html')

""""
@app.route('/mysqlmongo')
def words_import():
	words = g.mongodb.words
	g.mysql_cursor.execute("SELECT lemma FROM `words` ORDER BY wordid ASC LIMIT 8000,10")
	result = g.mysql_cursor.fetchall()
	finalresult = []
	for row in result:
		g.mysql_cursor.execute("SELECT pos,s.synsetid,sy.definition AS def FROM words AS w LEFT JOIN senses AS s ON s.wordid=w.wordid LEFT JOIN synsets AS sy ON sy.synsetid = s.synsetid WHERE w.lemma = '"+row['lemma']+"' ORDER BY pos,sensenum")
		wordinfo = []
		wordinforesult = g.mysql_cursor.fetchall()
		for word in wordinforesult:
			wordinfo.append(word)
		finalresult.append( {"lemma": row['lemma'], "gloss" : wordinfo})
	words.insert(finalresult)
	return 1
#	return render_template('resultsimport.html',entries=finalresult)"""

@app.route('/search', methods=['GET', 'POST'])
def search():
	word = ''
	result = {}
	if request.method == 'POST' :
		word = request.form['word']
	elif request.method == 'GET':
		word = request.args['word']
	word = word.strip()
	if(word!=''):
		
		words = g.mongodb.words
		entries = words.find_one({"lemma":word })
		
		if(entries==None):
			suggest=correct(word)
			if(suggest==None):
				return render_template('notfound.html')
			else:
				result["suggest"]=suggest
		else:
			result['suggest'] = ''

		result['entries']=entries		

		return render_template('results.html',result=result)
	else:
		return render_template('search.html')


if __name__ == '__main__':
    app.run()

