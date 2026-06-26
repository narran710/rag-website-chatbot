import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import hashlib
import xml.etree.ElementTree as ET


def get_page_text(url):

    response = requests.get(
        url,
        timeout=10,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "noscript",
        "svg",
        "form",
        "button",
        "input",
        "iframe"
    ]):
        tag.decompose()

            
    selectors = [

        "main",

        "article",

        '[role="main"]',

        "#content",

        ".content",

        ".documentation",

        ".docs"

    ]

    main_content = None

    for selector in selectors:

        main_content = soup.select_one(selector)

        if main_content:
            break

    if main_content is None:

        main_content = soup.body

    text = main_content.get_text(
        separator="\n"
    )

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return "\n".join(lines), soup


def crawl_website(start_url, max_pages=25):
    visited = set()

    queue = get_sitemap_urls(

        start_url,

        limit=max_pages

    )

    if not queue:

        queue = [start_url]

    content_hashes = set()

    Path("data/scraped_pages").mkdir(
        parents=True,
        exist_ok=True
    )

    visited = set()
    queue = [start_url]

    pages_scraped = 0

    while queue and pages_scraped < max_pages:

        current_url = queue.pop(0)
        print("Crawling:", current_url)
        if current_url in visited:
            continue

        try:

            text, soup = get_page_text(current_url)

            page_hash = hashlib.md5(
            text.encode("utf-8")
            ).hexdigest()

            if page_hash in content_hashes:
                continue

            content_hashes.add(page_hash)

            visited.add(current_url)

            pages_scraped += 1
            file_name = f"page_{pages_scraped}.txt"

            file_path = (
                Path("data/scraped_pages")
                / file_name
            )

            with open(
                file_path,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(f"URL: {current_url}\n\n")
                f.write(text)

            base_domain = urlparse(start_url).netloc

            for link in soup.find_all("a", href=True):

                next_url = urljoin(
                    current_url,
                    link["href"]
                ).split("#")[0]

                parsed = urlparse(next_url)

                if parsed.netloc == base_domain:
                    if next_url not in visited:
                        queue.append(next_url)

        except Exception:
            continue

    return {
        "pages_scraped": pages_scraped
    }

def get_sitemap_urls(start_url, limit=100):

    sitemap_url = urljoin(start_url, "/sitemap.xml")

    try:

        response = requests.get(

            sitemap_url,

            timeout=10,

            headers={"User-Agent": "Mozilla/5.0"}

        )

        response.raise_for_status()

        root = ET.fromstring(response.text)

        namespace = {

            "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"

        }

        urls = []

        for loc in root.findall(".//sm:loc", namespace):

            urls.append(loc.text.strip())

            if len(urls) >= limit:
                break

        print(f"Found {len(urls)} URLs in sitemap.")

        return urls

    except Exception:

        print("No sitemap found.")

        return []