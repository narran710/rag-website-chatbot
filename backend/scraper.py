import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import hashlib



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
        "header"
    ]):
        tag.decompose()

    main_content = (
        soup.find("main")
        or soup.find("article")
        or soup.find("body")
    )

    text = main_content.get_text(
        separator="\n"
    )

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return "\n".join(lines), soup


def crawl_website(start_url, max_pages=10):
    visited = set()
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