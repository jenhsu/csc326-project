#!/usr/bin/env python
from bottle import route, run


@route('/')
def hello():
    return '''
        <html>
            <body>
                <h1><title>Root Page</title></h1>
                <h2 style="text-align:center;"><a id="link" href="one">Page One link</a></h2>
                <a href="two">Page Two link</a>
                <p style="text-align:center;">This is the root page.</p>
                <p>Just testing :-*(@#*!<p>
                <p>Word one</p>
                <p style="color:red;">word three</p>
                <p style="color:blue;">word_four</p>
            </body>
        </html>
    '''


@route('/one')
def one():
    return '''
        <html>
            <body>
                <h1>Page One</h1>
                <p>Every novel is a mystery novel if you never finish it.</>
                <a href="two">Page Two link</a>
            </body>
        </html>
    '''


@route('/two')
def two():
    return '''
        <html>
            <body>
                <h1>Page Two</h1>
                <a href="three">Page Three link</a>
                <table>
                <tr>
                    <td>100</td>
                    <td>Word Two</td>
                    <td>300</td>
                </tr>
                <tr>
                    <td>400</td>
                    <td>Word Two</td>
                    <td>600</td>
                </tr>
                <tr>
                    <td>700</td>
                    <td>Word Two</td>
                    <td>900</td>
                </tr>
                </table>
            </body>
        </html>
    '''


@route('/three')
def three():
    return '''
        <html>
            <body>
                <h1>word one</h1>
                <h2>word two</h2>
                <h3>word three</h3>
                <h4>word four</h4>
                <h5>word five</h5>
                <h6>word six</h6>
            </body>
        </html>
    '''
run(host='localhost', port=8080)