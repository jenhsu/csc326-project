from bottle import route, run, request, get, post
from collections import OrderedDict
import operator, re
#import islice

#store dictionary history
globalDict = OrderedDict()

@route('/hello')
def hello():
	return "Hello World"


#search bar
@get('/search')
def search():
	
	return '''
     	<head><title>My Search</title>
      	</head>
	  	<body>
		<h1>Search</h1>
		<form action ="/search" method="post">
			Search: <input name="keywords" type="text"/>
			<input value = "Search" type="submit" />
		</form>
	'''

#search result
@post('/search')
def result():
    #post user input
	input = request.forms.get('keywords')
	htmlTable = parse_dict(input)
	
	#return user input and result and history table
	return "{}".format(search()) + ''' 
		<h2>Result</h2>
		<p>Search for \"''' + re.sub("\s\s+", " ", input) + ''' \"  {} </p>
		'''.format(htmlTable) + "{} </body>".format(getHistory())
    

#store result and history
def parse_dict(inputString):
	d = OrderedDict()
	lowerCaseString = re.sub("\s\s+", " ", inputString.strip().lower())
	print lowerCaseString
	wordArray = lowerCaseString.split(" ")
	for word in wordArray :
		#parse for input
		if word in d:
			d[word] += 1
		else:
			d[word] = 1

		#update history
		if word in globalDict:
			globalDict[word] += 1
		else:
			globalDict[word] = 1
		

	html = ''' 
			<table id="results">
			<tr>
 			<th>Word</th>
    		<th>Count</th> 
  			</tr>
			'''

	for word in d:
		html += "<tr><td>" + word + "</td><td>" + str(d[word]) + "</td></tr>"

	html += "</table>"
	return html


#print history
def getHistory():
	if globalDict == 0: return none
	#sort globalDict to top 20 searched words
	
	html = ''' 
			<h2>History</h2>
			<table id="History">
			<tr>
 			<th>Word</th>
    		<th>Count</th> 
  			</tr>
	'''
	
	dSorted = [(v,k) for k,v in globalDict.iteritems()]
	dSorted.sort(reverse=True)		# natively sort tuples by first element
	dSorted= dSorted[:20]		#get the top 20 of the list	
	for v,k in dSorted:
		html += "<tr><td> %s </td><td> %d </td></tr>" % (k,v)


	html += "</table>"
	return html


run(host='localhost', port=8080, debug=True)
