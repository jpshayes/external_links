import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import csv

# Function to check if a URL is absolute
def is_absolute(url):
    return bool(urlparse(url).netloc)

# Function to check if a URL is from the main domains (excluding subdomains)
def is_valid_domain(url, main_domains):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain in main_domains

# Function to check if a URL has a disallowed extension
def has_disallowed_extension(url, disallowed_extensions):
    return any(url.lower().endswith(ext) for ext in disallowed_extensions)

# Function to check if a URL path matches the disallowed pattern
def has_disallowed_path(url, disallowed_paths):
    path = urlparse(url).path
    return any(path.startswith(dp) for dp in disallowed_paths)

# Function to scrape links from a specified tag and save them to a CSV file
def scrape_and_save_links(url, valid_domains, log_domains, output_file, disallowed_extensions, disallowed_paths, visited=set()):
    # If the URL has already been visited, skip it
    if url in visited:
        print(f"Skipping already visited URL: {url}")
        return

    # Mark the URL as visited
    visited.add(url)
    print(f"Visiting URL: {url}")

    # Send a GET request to the URL
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except (requests.RequestException, requests.Timeout) as e:
        print(f"Failed to retrieve the page: {url}. Error: {e}")
        return

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the main tag with id="main-content"
    main_tag = soup.find('main', id='main-content')
    
    if main_tag:
        print(f"Found <main id='main-content'> tag in URL: {url}")
        # Find all <a> tags within the specified tag
        a_tags = main_tag.find_all('a', href=True)
        
        with open(output_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([f"Links found on {url}"])
            for a in a_tags:
                href = a['href']
                # Convert relative URLs to absolute URLs
                if not is_absolute(href):
                    href = urljoin(url, href)
                # Log the link if it's pointing to the specified log domains, does not have a disallowed extension, and is not in disallowed paths
                href_parsed = urlparse(href)
                if href_parsed.netloc in log_domains and not has_disallowed_extension(href, disallowed_extensions) and not has_disallowed_path(href, disallowed_paths):
                    writer.writerow([href])
                    print(f"Logged link: {href}")
            writer.writerow([])  # Blank row for separation
    else:
        print(f"No <main id='main-content'> tag found in URL: {url}")

    # Find all <a> tags on the page to continue crawling
    all_a_tags = soup.find_all('a', href=True)
    for a in all_a_tags:
        href = a['href']
        # Convert relative URLs to absolute URLs
        if not is_absolute(href):
            href = urljoin(url, href)
        # Continue crawling if the link is within the valid domains, does not have a disallowed extension, and is not in disallowed paths
        href_parsed = urlparse(href)
        if is_valid_domain(href, valid_domains) and not has_disallowed_extension(href, disallowed_extensions) and not has_disallowed_path(href, disallowed_paths) and href not in visited:
            scrape_and_save_links(href, valid_domains, log_domains, output_file, disallowed_extensions, disallowed_paths, visited)
            # Sleep to prevent overloading the server
            time.sleep(1)

# Example usage
url = 'https://www.indianastate.edu'
valid_domains = ['www.indianastate.edu', 'indianastate.edu']
log_domains = ['www.indstate.edu', 'indstate.edu']
output_file = 'filtered_links.csv'
disallowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx']
disallowed_paths = ['/profile/']

# Clear the output file before starting
with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Page URL', 'Links'])

scrape_and_save_links(url, valid_domains, log_domains, output_file, disallowed_extensions, disallowed_paths)
