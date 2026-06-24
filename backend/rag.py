from pathlib import Path
import re
import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

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

def chunk_text(
    text,
    chunk_size=500,
    overlap=100
):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += (
            chunk_size - overlap
        )

    return chunks

def create_chunks():

    input_dir = Path(
        "data/cleaned_pages"
    )

    output_dir = Path(
        "data/chunks"
    )

    output_dir.mkdir(
        exist_ok=True
    )

    total_chunks = 0

    for file_path in input_dir.glob("*.txt"):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            text = f.read()

        chunks = chunk_text(text)

        for idx, chunk in enumerate(chunks):

            chunk_data = {
                "source_file":
                    file_path.name,
                "chunk_id":
                    idx,
                "text":
                    chunk
            }

            chunk_file = (
                output_dir /
                f"{file_path.stem}_{idx}.json"
            )

            with open(
                chunk_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    chunk_data,
                    f,
                    indent=2
                )

            total_chunks += 1

    return total_chunks

def create_embeddings():

    chunks_dir = Path(
        "data/chunks"
    )

    embeddings_dir = Path(
        "data/embeddings"
    )

    embeddings_dir.mkdir(
        exist_ok=True
    )

    count = 0

    for chunk_file in chunks_dir.glob("*.json"):

        with open(
            chunk_file,
            "r",
            encoding="utf-8"
        ) as f:

            chunk_data = json.load(f)

        text = chunk_data["text"]

        embedding = (
            embedding_model
            .encode(text)
            .tolist()
        )

        output_data = {
            "source_file":
                chunk_data["source_file"],
            "chunk_id":
                chunk_data["chunk_id"],
            "text":
                text,
            "embedding":
                embedding
        }

        output_file = (
            embeddings_dir /
            chunk_file.name
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                output_data,
                f
            )

        count += 1
    
    return count

def build_faiss_index():

    embeddings_dir = Path(
        "data/embeddings"
    )

    vectors = []
    metadata = []

    for file_path in embeddings_dir.glob("*.json"):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        vectors.append(
            data["embedding"]
        )

        metadata.append({
            "source_file":
                data["source_file"],
            "chunk_id":
                data["chunk_id"],
            "text":
                data["text"]
        })

    if not vectors:
        return 0

    vectors = np.array(
        vectors,
        dtype=np.float32
    )

    faiss.normalize_L2(vectors)

    index = faiss.IndexFlatIP(
        dimension
    )
    index.add(vectors)

    Path(
        "data/faiss_index"
    ).mkdir(
        exist_ok=True
    )

    faiss.write_index(
        index,
        "data/faiss_index/index.faiss"
    )

    with open(
        "data/faiss_index/metadata.pkl",
        "wb"
    ) as f:

        pickle.dump(
            metadata,
            f
        )

    return len(metadata)

def retrieve_chunks(
        query,
        top_k=5
    ):
        
        index = faiss.read_index(
        "data/faiss_index/index.faiss"
    )

        with open(
            "data/faiss_index/metadata.pkl",
            "rb"
        ) as f:

            metadata = pickle.load(f)

        query_embedding = (
            embedding_model
            .encode(query)
            .reshape(1, -1)
            .astype(np.float32)
        )

        faiss.normalize_L2(query_embedding)
        
        distances, indices = index.search(
            query_embedding,
            top_k
        )

        results = []

        for idx, distance in zip(
            indices[0],
            distances[0]
        ):

            if idx < len(metadata):

                results.append({
                    "score":
                        float(distance),
                    "source_file":
                        metadata[idx]["source_file"],
                    "chunk_id":
                        metadata[idx]["chunk_id"],
                    "text":
                        metadata[idx]["text"]
                })

        return results