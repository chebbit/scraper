# RSS - scraper

<p> A simple scraper to receive news form RSS and put it in a database.<\p>

must be installed on the system:
- docker-compose 1.25.0
- python 3.7 with package click:

   <code>pip install -r requirements.txt</code>

<p>entry point for a user start.py </p>

<code>python start.py --help</code>

<p>Commands for work with service</p>
<p>Start server database and scraper</p> 
<code>python start.py start-server</code>

-   <p>Create schema and change scraper to new schema </p>
    <code>python start.py create-schema</code>

-   <p>Run scraper</p>
    <code>python start.py run-scraper</code>

-   <p>Export data to CSV, file will be save in folder output</p>
    <code>python start.py export</code>
    
___
This is a test is for a Python programmer position.
