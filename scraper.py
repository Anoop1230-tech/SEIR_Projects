print("=== SCRIPT STARTED ===")

import sys
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def normalize_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        return "https://" + url
    return url


def scrape_website(url):
    print("Raw input:", url)

    url = normalize_url(url)
    print("Normalized URL:", url)

    try:
        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch(headless=False)  # show browser for debugging
            page = browser.new_page()

            print("Opening page...")
            response = page.goto(url, timeout=60000, wait_until="networkidle")

            if response:
                print("Status Code:", response.status)
            else:
                print("No response received")

            html = page.content()
            print("HTML received. Length:", len(html))

            browser.close()

    except Exception as e:
        print("ERROR:", e)
        return

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    print("\n===== TITLE =====")
    if soup.title:
        print(soup.title.get_text(strip=True))
    else:
        print("No title found")

    print("\n===== BODY TEXT =====")
    if soup.body:
        print(soup.body.get_text(separator="\n", strip=True))
    else:
        print("No body text found")

    print("\n===== OUTLINKS =====")
    links = set()
    for a in soup.find_all("a", href=True):
        full_link = urljoin(url, a["href"])
        links.add(full_link)

    if links:
        for link in sorted(links):
            print(link)
    else:
        print("No links found")


def main():
    print("Arguments received:", sys.argv)

    if len(sys.argv) < 2:
        print("Usage: python scraper.py domain.com")
        return

    scrape_website(sys.argv[1])


if __name__ == "__main__":
    main()