from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from urllib.parse import urlparse
from backend.scraper import crawl_website
from backend.rag import (
    clean_documents,
    create_chunks,
    create_embeddings,
    build_faiss_index,
    retrieve_chunks
)

app = FastAPI(
    title="RAG Website Chatbot",
    version="1.0.0"
)


class URLRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    question: str


def is_valid_url(url: str):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


@app.get("/")
def root():
    return {
        "status": "running",
        "message": "RAG Website Chatbot Backend"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/ingest")
def ingest(data: URLRequest):

    if not is_valid_url(data.url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL"
        )

    crawl_result = crawl_website(
        data.url,
        max_pages=10
    )

    cleaned_count = clean_documents()

    chunk_count = create_chunks()

    embedding_count = create_embeddings()

    indexed_chunks =build_faiss_index()

    return {
        "status": "success",
        "pages_scraped": crawl_result["pages_scraped"],
        "documents_cleaned": cleaned_count,
        "chunks_created": chunk_count,
        "embeddings_created": embedding_count,
        "indexed_chunks": indexed_chunks
    }

@app.post("/retrieve")
def retrieve(
    data: QueryRequest
):

    results = retrieve_chunks(
        data.question
    )

    return {
        "question":
            data.question,
        "results":
            results}

