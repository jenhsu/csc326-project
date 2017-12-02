<!DOCTYPE html>
<html lang="en">
<head>
    <style>
        #container{
            padding-top: 2%;
            display: flex;
            flex-direction: column;
            text-align: center;
        }
        }
        #results{
            order: 1;
        }
        #pages{
            order: 2;
        }
        table{
            margin-left: auto;
            margin-right: auto;
        }
    </style>
</head>
<body>
    %if len(urls)==0:
        <p> No Results Found.</p>
        {{!suggestions}}
    %else:
    <div id="container">
        <div id="results">
            <table id="resultsTable">
                <tr><th>Retrieved URLs</th></tr>
                %for i in xrange(len(urls)):
                    %url = urls[i][0]
                    <tr><td><a href="{{url}}">{{url}}</a></td></tr>
                %end
            </table>
        </div>

        <div id="pages">
            <b>Pages: </b>
            %for i in xrange(1, total_pages + 1):
                %if i == curr_page:
                    <b>{{i}}</b>
                %else:
                    <a href="/search?keywords={{keywords}}&page_no={{i}}">{{i}}</a>
                %end
            %end
            %if curr_page < total_pages:
                <a href="/search?keywords={{keywords}}&page_no={{curr_page+1}}">Next</a>
            %end
        </div>
    </div>
    %end
</body>