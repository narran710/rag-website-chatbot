from pathlib import Path
import re
import json
from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder
from langchain_text_splitters import RecursiveCharacterTextSplitter
import faiss
import numpy as np
import pickle
from rank_bm25 import BM25Okapi
from groq import Groq
from dotenv import load_dotenv
import os
from transformers import (
    GPT2LMHeadModel,
    GPT2TokenizerFast
)
import torch
import math

load_dotenv()

groq_client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)

embedding_model = SentenceTransformer(
    "BAAI/bge-large-en-v1.5"
)

print("Loading Cross Encoder...")

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

print("Cross Encoder loaded.")

print("Loading GPT-2...")

tokenizer = GPT2TokenizerFast.from_pretrained(
    "gpt2"
)

perplexity_model = GPT2LMHeadModel.from_pretrained(
    "gpt2"
)

perplexity_model.eval()

print("GPT-2 loaded.")

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


splitter = RecursiveCharacterTextSplitter(

    chunk_size=800,

    chunk_overlap=150,

    separators=[

        "\n\n",

        "\n",

        ". ",

        " ",

        ""

    ]

)

def chunk_text(text):

    return splitter.split_text(text)

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
            .encode(
                text,
                normalize_embeddings=True,
                convert_to_numpy=True
            )
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

    dimension = vectors.shape[1]

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

    query_embedding = embedding_model.encode(

        query,

        normalize_embeddings=True,

        convert_to_numpy=True

    ).astype(np.float32)

    query_embedding = np.expand_dims(

        query_embedding,

        axis=0

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

                "score": float(distance),

                "cosine_similarity": round(
                    float(distance),
                    4
                ),

                "source_file":
                    metadata[idx]["source_file"],

                "chunk_id":
                    metadata[idx]["chunk_id"],

                "text":
                    metadata[idx]["text"]

            })

    return results

def retrieve_bm25(query, top_k=5):

    with open(
        "data/faiss_index/metadata.pkl",
        "rb"
    ) as f:
        metadata = pickle.load(f)

    corpus = [
        item["text"]
        for item in metadata
    ]

    tokenized_corpus = [
        doc.lower().split()
        for doc in corpus
    ]

    bm25 = BM25Okapi(
        tokenized_corpus
    )

    tokenized_query = (
        query.lower().split()
    )

    scores = bm25.get_scores(
        tokenized_query
    )

    ranked = np.argsort(
        scores
    )[::-1][:top_k]

    results = []

    for idx in ranked:

        results.append({
            "score": float(scores[idx]),
            "source_file": metadata[idx]["source_file"],
            "chunk_id": metadata[idx]["chunk_id"],
            "text": metadata[idx]["text"]
        })

    return results


def retrieve_hybrid(query, top_k=5):

    dense_results = retrieve_chunks(
        query,
        top_k=20
    )

    sparse_results = retrieve_bm25(
        query,
        top_k=20
    )

    # -----------------------------
    # Normalize BM25 scores
    # -----------------------------

    if sparse_results:

        scores = [

            item["score"]

            for item in sparse_results

        ]

        min_score = min(scores)

        max_score = max(scores)

        for item in sparse_results:

            if max_score == min_score:

                item["bm25_score"] = 1.0

            else:

                item["bm25_score"] = (

                    item["score"] - min_score

                ) / (

                    max_score - min_score

                )

    # -----------------------------
    # Merge Dense + Sparse
    # -----------------------------

    combined = {}

    for result in dense_results:

        key = (

            result["source_file"],

            result["chunk_id"]

        )

        combined[key] = {

            **result,

            "bm25_score": 0.0,

            "hybrid_score":

                0.7 *

                result["cosine_similarity"]

        }

    for result in sparse_results:

        key = (

            result["source_file"],

            result["chunk_id"]

        )

        if key in combined:

            combined[key]["bm25_score"] = result["bm25_score"]

            combined[key]["hybrid_score"] += (

                0.3 *

                result["bm25_score"]

            )

        else:

            combined[key] = {

                **result,

                "cosine_similarity": 0.0,

                "hybrid_score":

                    0.3 *

                    result["bm25_score"]

            }

    # -----------------------------
    # Sort by Hybrid Score
    # -----------------------------

    results = sorted(

        combined.values(),

        key=lambda x: x["hybrid_score"],

        reverse=True

    )

    # -----------------------------
    # Diversity Filtering
    # -----------------------------

    final_results = []

    used_files = set()

    for item in results:

        if item["source_file"] not in used_files:

            final_results.append(item)

            used_files.add(item["source_file"])

        if len(final_results) == top_k:

            break

    return final_results

def rerank_results(query, retrieved, top_k=5):

    if not retrieved:
        return []

    pairs = [

        (query, item["text"])

        for item in retrieved

    ]

    scores = reranker.predict(pairs)

    for item, score in zip(retrieved, scores):

        item["rerank_score"] = float(score)

    retrieved.sort(

        key=lambda x: x["rerank_score"],

        reverse=True

    )

    return retrieved[:top_k]

def build_context(results):

    context = []

    for result in results:

        context.append(
            f"""
Source: {result['source_file']}
Chunk: {result['chunk_id']}

{result['text']}
"""
        )

    return "\n-------------------------\n".join(context)

def calculate_perplexity(text):

    inputs = tokenizer(
        text,
        return_tensors="pt"
    )

    with torch.no_grad():

        outputs = perplexity_model(
            **inputs,
            labels=inputs["input_ids"]
        )

    loss = outputs.loss.item()

    perplexity = math.exp(loss)

    return round(
        perplexity,
        2
    )

import time

def generate_answer(question):

    start_time = time.time()

    retrieved = retrieve_hybrid(
        question,
        top_k=20
    )

    retrieved = rerank_results(
        question,
        retrieved,
        top_k=5
    )

    context_chunks = expand_parent_chunks(
        retrieved
    )

    print("\n========== RETRIEVED ==========\n")

    for i, item in enumerate(retrieved, 1):

        print(f"{i}. {item['source_file']} | Chunk {item['chunk_id']}")

        print(item["text"][:300])

        print("-" * 60)

    context = build_context(
        context_chunks
    )

    prompt = f"""
You are a Retrieval-Augmented Generation assistant.

Answer ONLY using the provided context.

You may summarize, combine and rephrase information from multiple context passages.

If the answer is partially available,
answer using the available information.

Only reply

I could not find that information.

if absolutely no relevant information exists.

====================

Context:

{context}

====================

Question:

{question}

Answer:
"""

    response = groq_client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0

    )

    answer = response.choices[0].message.content

    perplexity = calculate_perplexity(answer)

    response_time = round(
        time.time() - start_time,
        3
    )

    scores = [

        item["cosine_similarity"]

        for item in retrieved

        if "cosine_similarity" in item

    ]

    average_similarity = round(

        sum(scores) / len(scores),

        4

    ) if scores else 0

    retrieval_confidence = round(

        average_similarity * 100,

        1

    )

    return {

        "answer": answer,

        "perplexity": perplexity,

        "response_time": response_time,

        "average_similarity": average_similarity,

        "retrieval_confidence": retrieval_confidence,

        "embedding_model": "BAAI/bge-large-en-v1.5",

        "retrieved_chunks": len(retrieved),

        "retrieval": "Hybrid (FAISS + BM25 + Cross Encoder)",

        "sources": [

            {

                "source_file": item["source_file"],

                "chunk_id": item["chunk_id"],

                "score": item.get("score"),

                "cosine_similarity": item.get("cosine_similarity"),

                "rerank_score": item.get("rerank_score"),

                "hybrid_score": item.get("hybrid_score"),

                "bm25_score": item.get("bm25_score")

            }

            for item in retrieved
        ]
    }

def expand_parent_chunks(retrieved):

    with open(
        "data/faiss_index/metadata.pkl",
        "rb"
    ) as f:

        metadata = pickle.load(f)

    metadata_lookup = {}

    for item in metadata:

        metadata_lookup[
            (
                item["source_file"],
                item["chunk_id"]
            )
        ] = item

    expanded = []

    seen = set()

    for item in retrieved:

        source = item["source_file"]

        chunk = item["chunk_id"]

        for offset in (-1, 0, 1):

            key = (
                source,
                chunk + offset
            )

            if (
                key in metadata_lookup
                and key not in seen
            ):

                expanded.append(

                    metadata_lookup[key]

                )

                seen.add(key)

    expanded.sort(

        key=lambda x: (

            x["source_file"],

            x["chunk_id"]

        )

    )

    return expanded