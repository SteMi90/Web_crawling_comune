import requests
from bs4 import BeautifulSoup, Comment
import re
from collections import deque
from urllib.parse import urljoin
import time
import os

def text_from_html(soup):
    "Estrae il testo visibile da un oggetto BeautifulSoup"
    [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
    return soup.get_text()

def find_target_words(soup, words):
    text = text_from_html(soup).lower()

    found_words = []
    for word in words:
        if re.search(r'\b' + re.escape(word.lower()) + r'\b', text):
            found_words.append(word)

    return found_words



def get_links(soup, base_url):
    links = set()
    for link in soup.find_all('a', href=True):
        url = link['href']
        if not url.startswith('http'):
            url = urljoin(base_url, url)
        links.add(url)
    return links

def save_page(soup, word, output_dir):
    timestamp = int(time.time())
    file_name = f"{word}_{timestamp}.html"
    file_path = os.path.join(output_dir, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

def main():
    start_url = "https://www.comune.senigallia.an.it/"
    target_words = ["ciclovia", "pista ciclabile"]
    output_dir = "saved_pages"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    visited_urls = set()
    url_queue = deque([start_url])

    while url_queue:
        current_url = url_queue.popleft()

        if current_url in visited_urls:
            continue  

        visited_urls.add(current_url)

        try:
            response = requests.get(current_url, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                found_words = find_target_words(soup, target_words)

                if found_words:
                    print(f"Found target words in {current_url}:")
                    for word in found_words:
                        print(f"- {word}")
                        save_page(soup, word, output_dir)
                        print(f"Saved {current_url} as {word}_{int(time.time())}.html")

                new_links = get_links(soup, current_url)
                url_queue.extend([link for link in new_links if link not in visited_urls])
            else:
                print(f"Error: Unable to fetch {current_url}. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error: Unable to fetch {current_url}. Exception: {e}")

if __name__ == "__main__":
    main()
