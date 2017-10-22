from bottle import route, run, request, static_file, redirect, app, template
import copy
from collections import OrderedDict, deque
from collections import Counter
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from beaker.middleware import SessionMiddleware
#from beaker.cache import cache_regions
import re, httplib2
import os


# store dictionary user history
global_user_history = dict()
global_user_recent = dict()
global_dict = Counter()
recent_history = deque(maxlen=10)

#check if user is signed in or not
anonymous = ""

SCOPE = 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email'
REDIRECT_URI = "http://localhost:8080/redirect"
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
    """Returns results page with search data and history."""
    s = request.environ.get('beaker.session')
    result_page = search_page()

    # Get user input if any exist
    if 'keywords' in request.query:
        input = request.query['keywords']
        if input.strip():
            html_table = parse_dict(input)
            # return user input and result and history table
            result_page +='''
                <p>Search for \"''' + re.sub("\s\s+", " ", input) + '''\"</p><div id="table_container"> {}
                    '''.format(html_table) + "</div>"

        # display history and recent history only if user signed in
        if anonymous == False:
            result_page += '''<div id="table_container"> {}'''.format(get_history()) + "</div>" + '''<div id="table_container"> {}'''.format(get_recent()) + "</div>"
    return result_page

@route('/signout')
def logout():
    """user signs out"""
    global anonymous
    anonymous = True
    s = request.environ.get('beaker.session')

    #copy history and recent history
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

    try:
        if s['email']:
            email = s['email']
            if s['picture']:
                picture = s['picture']
            if s['name']:
                name = s['name']
        return template('search', anonymous=anonymous, picture=picture, name=name, email=email)
    except:
        return template('search', anonymous=anonymous)


@route('/static/<filename:path>')
def server_static(filename):
    """Serves static files from project directory."""
    return static_file(filename, root=os.path.dirname(os.path.realpath(__file__)))

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


run(host='localhost', port=8080, debug=True, app=app)
