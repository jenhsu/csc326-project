import copy
import os
import re
import sqlite3 as sql
from collections import Counter
from collections import OrderedDict, deque, defaultdict
from math import ceil

from autocorrect import spell
from beaker.middleware import SessionMiddleware
from bottle import route, run, request, static_file, redirect, app, template, error

from cache import LRUCache

# store dictionary user history
global_user_history = dict()
global_user_recent = dict()
global_dict = Counter()
recent_history = deque(maxlen=10)
global_suggest = []
# Initialize custom LRU Cache with a capacity of 10000 search results.
global_search_cache = LRUCache(10000)

BASE_URL = "http://ec2-34-237-5-126.compute-1.amazonaws.com"
REDIRECT_URI = BASE_URL + "/redirect"

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
    s = request.environ.get('beaker.session')
    return search_page()


@route('/search')
def result():
    """Returns search results page."""
    s = request.environ.get('beaker.session')
    result_page = search_page()

    # Get user input if any exist
    if 'keywords' in request.query:
        if 'page_no' not in request.query:
            redirect("{0}/search?{1}".format(BASE_URL, request.query_string + "&page_no=1"))
        # Choose the first word as the search keyWord.
        keywords = request.query['keywords']
        page = int(request.query['page_no'])
        urls, suggest_html, spell_check_html = search_keywords(keywords)
        result_page += spell_check_html
        page_urls = urls[5 * (page - 1): 5 * page]
        total_pages = int(ceil(len(urls) / 5.0))
        result_page += template('search_results', urls=page_urls, curr_page=page,
                                total_pages=total_pages,
                                keywords="+".join(keywords.split()),
                                suggestions=suggest_html)

    return result_page


def search_keywords(keywords):
    """ Execute an SQL query for each word in keywords and return an array of
        (url, pagerank_score) pairs sorted by decreasing pagerank_score.

        Args:
            keywords: keywords string to be searched.
        Returns:
            urls: Array of (url, pagerank_score) pairs sorted by decreasing
                pagerank score.
            suggest_html: HTML content for search suggestions
            spell_check_html: HTML content for autocorrected keywords results.
        """
    suggest_html = ''
    spell_check_html = ''
    # First check for search string in LRU search cache
    urls = global_search_cache.get(keywords)
    if urls is None:
        con = sql.connect('dbFile.db')
        cur = con.cursor()
        urls = query_words(keywords, cur)
        global_search_cache.set(keywords, urls)
        # if no results, try to auto-correct keywords and search again
        if len(urls) == 0:
            spell_check_html, check_keywords = spell_check(keywords)
            # If auto-correct made changes, query the corrected string.
            if spell_check_html:
                urls = query_words(check_keywords, cur)
                # corrected keywords has results
                if len(urls) == 0:
                    spell_check_html = ""
                else:
                    # Remove keywords from cache to trigger auto-correct on next
                    # call.
                    global_search_cache.set(keywords, None)
                    # save valid corrected search in suggestions list
                    if check_keywords not in global_suggest:
                        global_suggest.append(check_keywords)
                # corrected keywords has no results, display suggestions list
        else:
            # save non-empty search in suggestions list
            if keywords not in global_suggest:
                global_suggest.append(keywords)
        con.close()
    if not urls:
        suggest_html = suggestions(keywords, global_suggest)
    return urls, suggest_html, spell_check_html


def query_words(keywords, cur):
    """ Execute an SQL query for each word in keywords and return an array of
    (url, pagerank_score) pairs sorted by decreasing pagerank_score.

    Args:
        keywords: keywords string to be searched.
        cur: cursor for the database connection.
    Returns:
        urls: Array of (url, pagerank_score) pairs sorted by decreasing pagerank
            score.
    """
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
    return sorted(results.items(), key=lambda x: x[1], reverse=True)


def spell_check(input):
    """Autocorrect the input string

        Args:
        input: Query string input.
    """
    html = ""
    input = re.sub("\s\s+", " ", input.strip().lower())
    word_array = input.split(" ")
    temp = ''
    for word in word_array:
        correct = spell(word)
        temp += correct + ' '

    temp = temp.rstrip()
    if input.lower() != temp.lower():
        html += '''<p> No result for \"''' + re.sub("\s\s+", " ", input) +\
        '''\"</p><p>Showing search results for \"''' + re.sub("\s\s+", " ", temp) + '''\"</p>'''
    return html,temp


def suggestions(input, history):
    """Prints a search suggestions table if input from user give no results

        Args:
        input: Query string input.
        history: global list of successfully searched terms
    """
    suggestions = []
    pattern = ''

    if len(input) == 1:
        pattern = '^' + input
    else:
        for word in input.split():
            pattern += '.*'.join(word[0] + word[-1]) + ' +'
            pattern = '^' + pattern
    pattern = pattern[:-2]

    regex = re.compile(pattern)
    for string in history:
        match = regex.search(string)
        if match:
            suggestions.append(string)

    html = '''
               <table id="Suggestions">
               <tr><th style="text-align:center">Search Suggestions</th></tr>
            '''
    if not suggestions:
        html = ''
    else:
        for item in suggestions[:5]:
            html += "<tr><td>" + item + "</td></tr>"
        html += "</table>"
    return html


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
    """Return contents of an error page."""
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
