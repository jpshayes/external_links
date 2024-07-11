# Link Scraper and Logger

This Python script scrapes links from the website `https://www.indianastate.edu`, logs only the links pointing to `www.indstate.edu` and `indstate.edu` (excluding other subdomains), and writes the results to a CSV file, grouped by the URL they were found on. The script specifically looks for links within the `<main id="main-content">` tag and skips URLs with certain disallowed paths and extensions.

## Requirements

The following Python libraries are required:
- `requests`
- `beautifulsoup4`

You can install the required libraries using the provided `requirements.txt` file:

```sh
pip install -r requirements.txt

