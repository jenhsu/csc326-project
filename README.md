CSC326 Lab2 README
==================
Package Contents
----------------
The project has the following directory structure:
- frontend.py: Frontend implementation built using bottle framework.
- client_secrets.json: stores Google API OATH2.0 parameters.
- views: folder containing frontend bottle templates.
    - search.tpl: search page template.
- logo.jpg: **DinoSaurch** search engine logo.
- requirements.txt: Python package dependencies.
- crawler.py: Crawler implementation built on top of starter code.
- dbFile.db: Database file containing results from crawler.
- urls.txt: Test URLs for manually verifying crawler functionality.
- tests: folder containing unit tests and fixtures.
    - crawler_test.py: Automated unit tests for crawler.
    - test_server.py: Test server with custom HTML to facilitate unit testing.
    - test_urls.txt: URLs for crawler to crawl in unit tests.

Running Backend
---------------
Run **python crawler.py** to run crawler against urls in urls.txt. This produces
a dbFile.db file containing the Lexicon, Inverted Index, PageRank, and Doc Index
tables.

Public IP Address
-----------------
http://ec2-34-237-5-126.compute-1.amazonaws.com

Benchmark Setup
---------------
Benchmark runs from a separate AWS t2.micro instance in the same region.
Asynchronous event processing is enabled by Bjoern.
Benchmark Command: ab -n 2500 -c 2500 -r http://ec2-34-237-5-126.compute-1.amazonaws.com/?keywords=helloworld+foo+bar
Benchmark Command: dstat
See **RESULT.pdf** for benchmark results.

Benchmark Comparison with Lab 2
-------------------------------
Benchmark results for Lab2 and Lab3 are very similar. This is expected because 
our database tables are very small and we make a single simple query per request.
From results of **percentage of the requests served within a certain time**,
we see that the Lab3 implementation is slightly slower. This is expected because
we are opening and closing a database connection on each request. The OS should cache the db file in memory, thus we don't see significantly higher
higher disk read totals.