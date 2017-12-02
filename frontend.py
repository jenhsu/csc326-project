import copy
import httplib2
import os
import re
import sqlite3 as sql
from collections import Counter
from collections import OrderedDict, deque, defaultdict
from math import ceil

from beaker.middleware import SessionMiddleware
from bottle import route, run, request, static_file, redirect, app, template, error
from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets

from cache import LRUCache

# store dictionary user history
global_user_history = dict()
global_user_recent = dict()
global_dict = Counter()
recent_history = deque(maxlen=10)
# Initialize custom LRU Cache with a capacity of 10000 search results.
global_search_cache = LRUCache(10000)

#check if user is signed in or not
anonymous = ""

SCOPE = 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email'
BASE_URL = "http://ec2-34-237-5-126.compute-1.amazonaws.com"
REDIRECT_URI = BASE_URL + "/redirect"
CLIENT_ID = "689107597559-4uoj4ucpa8c4ntm0jpiapnrasj4ecohl.apps.googleusercontent.com"
CLIENT_SECRET = "QE8cFRbbubTPhztL7vf5aTZr"



session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(app(), session_opts)

@route('/')
def home():
    """home page of web application"""
    global anonymous
    s = request.environ.get('beaker.session')

    if 'email' in s:
        anonymous = False
    else:
        anonymous = True
    return search_page()

@route('/login')
def login():
    """Google API login page"""
    global anonymous
    anonymous = False

    flow = flow_from_clientsecrets("client_secrets.json",
    scope= SCOPE,
    redirect_uri=REDIRECT_URI)
    uri = flow.step1_get_authorize_url()
    redirect(str(uri))

@route('/redirect')
def redirect_page():
    global global_dict
    global recent_history
    code = request.query.get('code', '')
    flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                               client_secret=CLIENT_SECRET,
                               scope=SCOPE,
                               redirect_uri=REDIRECT_URI)
    credentials = flow.step2_exchange(code)
    token = credentials.id_token['sub']

    #retreive user data from access token
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Get user info
    users_service = build('oauth2', 'v2', http=http)
    user_document = users_service.userinfo().get().execute()
    user_email = user_document['email']
    user_name = user_document['name']
    user_picture = user_document['picture']

    #Save user info
    s = request.environ.get('beaker.session')
    s['email'] = user_email
    s['name'] = user_name
    s['picture'] = user_picture
    s.save()

    #load user history
    if user_email in global_user_history:
        global_dict = global_user_history[user_email]
    else:
        global_user_history[user_email] = global_dict

    #load user recent history
    if user_email in global_user_recent:
        recent_history = global_user_recent[user_email]
    else:
        global_user_recent[user_email] = recent_history

    redirect('/search')

@route('/search')
def result():
    """Returns search results page."""
    s = request.environ.get('beaker.session')
    result_page = search_page()

    # Get user input if any exist
    if 'keywords' in request.query:
        """
        if input.strip():
            html_table = parse_dict(input)
            # return user input and result and history table
            result_page +='''
                <p>Search for \"''' + re.sub("\s\s+", " ", input) + '''\"</p><div id="table_container"> {}
                    '''.format(html_table) + "</div>"

        # display history and recent history only if user signed in
        if anonymous == False:
            result_page += '''<div id="table_container"> {}'''.format(get_history()) + "</div>" + '''<div id="table_container"> {}'''.format(get_recent()) + "</div>"
        """
        if 'page_no' not in request.query:
            redirect("{0}/search?{1}".format(BASE_URL, request.query_string + "&page_no=1"))
        keywords = request.query['keywords']
        # Choose the first word as the search keyWord.
        page = int(request.query['page_no'])
        con = sql.connect('dbFile.db')
        cur = con.cursor()
        urls = global_search_cache.get(keywords)
        if urls is None:
            print "CACHE MISS"
            results = defaultdict(float)
            for keyword in keywords.split():
                # No need to order by pageRank.score DESC with multi-word search
                query = """
                        SELECT DISTINCT docIndex.url, pageRank.score
                        FROM pageRank, lexicon, invertedIndex, docIndex
                        WHERE lexicon.word = "%s"
                            AND invertedIndex.wordid = lexicon.wordid
                            AND invertedIndex.docid = pageRank.docid
                            AND docIndex.docid = pageRank.docid
                        """ % keyword.lower()
                cur.execute(query)
                urls = cur.fetchall()
                for url, score in urls:
                    results[url] += score
            con.close()
            urls = sorted(results.items(), key=lambda x: x[1], reverse=True)
            global_search_cache.set(keywords, urls)
        page_urls = urls[5 * (page - 1): 5 * page]
        total_pages = int(ceil(len(urls) / 5.0))
        result_page += template('search_results', urls=page_urls, curr_page=page,
                                total_pages=total_pages,
                                keywords="+".join(keywords.split()))
    return result_page


@route('/signout')
def logout():
    """user signs out"""
    global anonymous
    anonymous = True
    s = request.environ.get('beaker.session')

    #copy history and recent history
    if 'email' in s:
        global_user_history[s['email']] = copy.copy(global_dict)
        global_user_recent[s['email']] = copy.copy(recent_history)
    s.delete()
    global_dict.clear()
    recent_history.clear()

    #redirect back to home page
    redirect('/')

def search_page():
    """Returns page with search bar, prompt query, and logo"""
    s = request.environ.get('beaker.session')

    if all(k in s for k in ('email', 'picture', 'name')):
        return template('search', anonymous=anonymous, picture=s['picture'], name=s['name'], email=s['email'])
    else:
        return template('search', anonymous=True)


@route('/static/<filename:path>')
def server_static(filename):
    """Serves static files from project directory."""
    return static_file(filename, root=os.path.dirname(os.path.realpath(__file__)))


@error(404)
def error404(error):
    return 'The requested page or file does not exist. <a href="{}">Click to search again.</a>'.format(BASE_URL)

def parse_dict(input_string):
    """Stores results, history in a dict and recently search in a deque and returns the results table.

    Args:
        input_string: Query string input.
    """
    d = OrderedDict()
    # take care of extra spaces and upper case char
    lower_case_string = re.sub("\s\s+", " ", input_string.strip().lower())
    word_array = lower_case_string.split(" ")
    for word in word_array:
        # parse for input
        if word in d:
            d[word] += 1
        else:
            d[word] = 1

        #update history and recently search words only if user is signed in
        if anonymous == False:
            # update history
            if word in global_dict:
                global_dict[word] += 1
            else:
                global_dict[word] = 1

            # update recently searched words
            if recent_history.count(word) == 0:
                if len(recent_history) == 10:
                    recent_history.popleft()
                recent_history.append(word)

    #prints result table
    html = '''
               <table id="results">
               <tr><th>Results</th></tr>
               <tr>
               <th>Word</th>
               <th>Count</th>
               </tr>
            '''

    for word in d:
        html += "<tr><td>" + word + "</td><td>" + str(d[word]) + "</td></tr>"

    html += "</table>"
    return html


def get_history():
    """Prints history of the top 20 search keywords in a table."""
    if not global_dict:
        return ""

    html = '''
               <table id="History">
               <tr><th style="text-align:center">History</th></tr>
               <tr>
               <th>Word</th>
               <th>Count</th>
               </tr>
            '''

    for k, v in global_dict.most_common(20):
        html += "<tr><td> %s </td><td> %d </td></tr>" % (k, v)

    html += "</table>"
    return html

def get_recent():
    """Print recently search top 10 words"""
    if not recent_history:
        return ""

    html = '''
               <table id="recent">
               <tr><th>Most Recent</th></tr>
               <tr>
               <th>Word</th>
               </tr>
            '''

    for word in reversed(recent_history):
        html += "<tr><td>" + word+ "</td></tr>"

    html += "</table>"
    return html

run(host='0.0.0.0', port=80, debug=True, app=app, server='bjoern')
