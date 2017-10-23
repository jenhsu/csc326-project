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
- urls.txt: Test URLs for manually verifying crawler functionality.
- tests: folder containing unit tests and fixtures.
    - crawler_test.py: Automated unit tests for crawler.
    - test_server.py: Test server with custom HTML to facilitate unit testing.
    - test_urls.txt: URLs for crawler to crawl in unit tests.

Public IP Address
-----------------
http://ec2-34-237-5-126.compute-1.amazonaws.com

Enabled Google APIs
-------------------
- Account Name
- Account Email
- Account Picture

Benchmark Setup
---------------
Benchmark runs from a separate AWS t2.micro instance in the same region.
Asynchronous event processing is enabled by Bjoern.
Benchmark Command: ab -n 2500 -c 2500 -r http://ec2-34-237-5-126.compute-1.amazonaws.com/?keywords=helloworld+foo+bar
Benchmark Command: dstat