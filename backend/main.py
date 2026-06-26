from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from urllib.parse import urlparse
from backend.scraper import crawl_website
from backend.rag import (
    clean_documents,
    create_chunks,
    create_embeddings,
    build_faiss_index,
    retrieve_hybrid,
    generate_answer
)
from fastapi.middleware.cors import CORSMiddleware
from backend.pdf_export import create_chat_pdf
from fastapi.responses import Response

class ExportPDFRequest(BaseModel):
    messages: list
    
app = FastAPI(
    title="RAG Website Chatbot",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://rag-website-chatbot-nu.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

    print("Step 1: Crawling...")
    crawl_result = crawl_website(
        data.url,
        max_pages=25
    )

    print("Step 2: Cleaning...")
    cleaned_count = clean_documents()

    print("Step 3: Chunking...")
    chunk_count = create_chunks()

    print("Step 4: Creating embeddings...")
    embedding_count = create_embeddings()

    print("Step 5: Building FAISS index...")
    indexed_chunks = build_faiss_index()

    print("✅ Ingestion complete!")

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

    results = retrieve_hybrid(
        data.question
    )

    return {
        "question":
            data.question,
        "results":
            results}

@app.post("/chat")
def chat(
    data: QueryRequest
):

    result = generate_answer(
        data.question
    )

    return result

@app.post("/export-pdf")
def export_pdf(
    data: ExportPDFRequest
):

    pdf = create_chat_pdf(
        data.messages
    )

    return Response(

        content=pdf,

        media_type="application/pdf",

        headers={

            "Content-Disposition":
            "attachment; filename=Conversation.pdf"

        }

    )