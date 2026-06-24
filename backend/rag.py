from pathlib import Path
import re


NOISE_PATTERNS = [
    "Skip to content",
    "Donate",
    "Menu",
    "Smaller",
    "Larger",
    "Reset",
    "GO",
    "Notice:",
    "This page displays a fallback"
]


def clean_text(text):

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if len(line) < 3:
            continue

        skip = False

        for pattern in NOISE_PATTERNS:
            if pattern.lower() in line.lower():
                skip = True
                break

        if skip:
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()

def clean_documents():

    input_dir = Path(
        "data/scraped_pages"
    )

    output_dir = Path(
        "data/cleaned_pages"
    )

    output_dir.mkdir(
        exist_ok=True
    )

    cleaned_count = 0

    for file_path in input_dir.glob("*.txt"):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            raw_text = f.read()

        cleaned_text = clean_text(
            raw_text
        )

        output_file = (
            output_dir /
            file_path.name
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(cleaned_text)

        cleaned_count += 1

    return cleaned_count