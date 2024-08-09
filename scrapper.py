import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from config import HEADERS, UNWANTED_PHRASES, BOILERPLATE_TERMS, MAX_SEGMENT_LENGTH
from utils import remove_html_tags, clean_text, filter_unwanted_content, normalize_text, remove_boilerplate, segment_text

def is_internal_link(url, base_url):
    parsed_base = urlparse(base_url)
    parsed_url = urlparse(url)

    # Normalize base URL
    base_netloc = parsed_base.netloc or parsed_base.path
    url_netloc = parsed_url.netloc or parsed_url.path

    return (parsed_url.scheme in ('http', 'https', '') and
            (url_netloc == base_netloc or url_netloc.endswith('.' + base_netloc.split('.')[-1])))

def clean_and_prepare_data(content):
    content = remove_html_tags(content) #removes html tags including images
    content = clean_text(content)
    content = filter_unwanted_content(content, UNWANTED_PHRASES)
    content = normalize_text(content)
    content = remove_boilerplate(content, BOILERPLATE_TERMS)
    return segment_text(content, MAX_SEGMENT_LENGTH)

def get_internal_links_and_content(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return set(), ""

    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = url
    page_content = soup.prettify()

    cleaned_content = clean_and_prepare_data(page_content)
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)

        if is_internal_link(full_url, base_url):
            cleaned_url = full_url.split('#')[0]
            title = (soup.title.string if soup.title else "").strip()
            print(f"Found internal link: {cleaned_url} (Title: {title})")
            links.add((cleaned_url, title))

    return links, cleaned_content

def save_as_jsonl(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for entry in data:
            json.dump(entry, f)
            f.write('\n')

def scrape_website(base_url):
    visited = set()
    to_visit = {base_url}
    all_links = set()
    all_data = []

    while to_visit:
        current_url = to_visit.pop()
        if current_url not in visited:
            print(f"Scraping {current_url}")
            visited.add(current_url)

            internal_links, content = get_internal_links_and_content(current_url)
            all_links.update(internal_links)
            to_visit.update(link for link, _ in internal_links if link not in visited)

            for segment in content:
                all_data.append({"url": current_url, "content": segment})

    save_as_jsonl(all_data, "scrapped_data.jsonl")

if __name__ == "__main__":
    base_url = "example.com" #add a real url before running the program
    scrape_website(base_url)
