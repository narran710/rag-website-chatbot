import requests
from bs4 import BeautifulSoup
from pathlib import Path


def scrape_page(url):
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        cleaned_text = "\n".join(lines)

        Path("data/scraped_pages").mkdir(
            parents=True,
            exist_ok=True
        )

        file_path = "data/scraped_pages/page_1.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        return {
            "success": True,
            "file_path": file_path,
            "characters": len(cleaned_text)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }