CSC326 Lab2 README
==================
Package Contents
----------------
The project has the following directory structure:
- frontend.py: Frontend implementation built using bottle framework.
- client_secrets.json: stores Google API OATH2.0 parameters.
- views: folder containing frontend bottle templates.
    - search.tpl: search page template.
    - search_results.tpl: url results template.
    - css.tpl: css template for search_results
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

Running Frontend
---------------
Run **python frontend.py <server_ip_address>** to launch the webserver.

Launching Script:
-------------------------------
First, run pip install paramiko to install the paramiko library. To launch the instance, compress everything in the directory to a file named csc326-project.tar.gz. In the same directory, write your AWS credentials on the first line of credentials.csv in the following format: <aws_access_key_id>,<aws_secret_access_key>, and run aws_setup.py. When script finishes, the public IP and DNS will be printed to the screen and returned, which can then be used to access the website. 

Termination Script:
-------------------------------
To terminate, first acquire the instances ID you are about to terminate either through EC2 console, or through boto api calls. Then in shell run >python aws_terminate.py <your_instance_id>. If there is no error (return value is 1) then the instance terminated with no error
