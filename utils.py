import re
from bs4 import BeautifulSoup

def remove_html_tags(text):
    return BeautifulSoup(text, "html.parser").text

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    return text.strip()

def filter_unwanted_content(text, unwanted_phrases):
    for phrase in unwanted_phrases:
        text = text.replace(phrase, '')
    return text

def normalize_text(text):
    return text.lower()  # Example normalization: convert to lowercase

def remove_boilerplate(text, boilerplate_terms):
    for term in boilerplate_terms:
        text = re.sub(term, '', text, flags=re.IGNORECASE)
    return text

def segment_text(text, max_length):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]
