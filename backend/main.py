from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from urllib.parse import urlparse

app = FastAPI(
    title="RAG Website Chatbot",
    version="1.0.0"
)


class URLRequest(BaseModel):
    url: str


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

    return {
        "status": "success",
        "message": "URL accepted",
        "url": data.url
    }