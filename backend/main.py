from fastapi import FastAPI

app = FastAPI(
    title="RAG Website Chatbot",
    version="1.0.0"
)


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