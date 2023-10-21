# Cial Web Scraper

This script takes in an URL and returns the phone numbers found on the website as well as the logo of the website(company, institution...).

## Running

Run "extract.py" imputing the url of the page to be scraped.

Example: "python3 extract.py https://illion.com.au"

## Limitations

- Should be tested on large number of cases to check if heuristic to identify phone numbers and find logos is complete
- While the existing code covers as many formats of phone number the author encountered, both false positives and false negatives can occur

- Function get_numbers() should be refactored and broken down into smaller functions

- Some websites have more advanced measures that block them from being scraped; this script will not work on those websites

- Script will not scrape phone numbers that are embedded as pictures and success on websites that used Flash or dynamic generations trough javasript is questionable

## Installation of dependencies

pip install -r requirements.txt

This installs all of the packages that don't come default with a python installation (https://docs.python.org/3/py-modindex.html) namely BeautifullSoup, html5lib and requests
