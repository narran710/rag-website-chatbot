# 🌐 RAG Website Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that crawls websites, builds a searchable knowledge base, and answers user questions using hybrid retrieval and Large Language Models.

---

# 📌 Features

* 🌍 Live Website Ingestion
* 🕸️ Recursive Website Crawling
* 🧹 Automatic Text Cleaning
* ✂️ Intelligent Text Chunking
* 🔎 Hybrid Retrieval (FAISS + BM25)
* 🤖 Cross-Encoder Re-ranking
* 💬 AI-powered Question Answering using Groq LLM
* 📄 Source Citations
* 📊 Cosine Similarity Metrics
* 📥 Export Chat History as PDF
* 🎨 Modern React Interface

---

# 🚀 Workflow

1. Enter a website URL.
2. Crawl the website recursively.
3. Clean and preprocess the extracted content.
4. Split the content into semantic chunks.
5. Generate vector embeddings.
6. Build a FAISS vector index.
7. Ask questions about the website.
8. Receive AI-generated answers with source citations.

---

# 🏗️ Architecture

```text
Website URL
      │
      ▼
Website Crawler
      │
      ▼
Text Cleaning
      │
      ▼
Chunking
      │
      ▼
Embedding Generation
      │
      ▼
FAISS Vector Store
      │
      ▼
Hybrid Retrieval
 (FAISS + BM25)
      │
      ▼
Cross-Encoder Re-ranking
      │
      ▼
Groq LLM
      │
      ▼
Generated Answer
```

---

# 🛠️ Tech Stack

## Frontend

* React
* Vite
* Axios
* CSS

## Backend

* FastAPI
* Python

## AI & NLP

* BAAI/bge-small-en-v1.5
* Cross Encoder (MS MARCO MiniLM)
* Groq API

## Retrieval

* FAISS
* BM25

## Libraries

* BeautifulSoup
* Requests
* LangChain Text Splitters
* NumPy
* ReportLab

---

# 📂 Project Structure

```text
rag-website-chatbot/

│
├── backend/
│   ├── main.py
│   ├── rag.py
│   ├── scraper.py
│   ├── cleaner.py
│   ├── chunker.py
│   ├── pdf_export.py
│   └── utils.py
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── styles/
│   └── api.js
│
├── data/
│   ├── cleaned_pages/
│   ├── chunks/
│   ├── embeddings/
│   └── faiss_index/
│
├── requirements.txt
└── README.md
```

---

# 📊 Retrieval Pipeline

The chatbot combines lexical and semantic retrieval to improve answer quality.

1. Query Embedding
2. FAISS Vector Search
3. BM25 Keyword Search
4. Merge Retrieved Results
5. Cross-Encoder Re-ranking
6. Groq LLM Answer Generation

---

# 📥 PDF Export

Users can export chat conversations as a PDF containing:

* User Questions
* AI Responses
* Source References

---

# 📈 Future Improvements

* Background website ingestion
* Streaming responses
* Multi-document support
* Persistent vector database
* Authentication and user management
* Website change detection
* Docker support
* Cloud deployment optimization

---

# 📚 Learning Outcomes

This project demonstrates practical implementation of:

* Retrieval-Augmented Generation (RAG)
* Semantic Search
* Vector Databases
* Embedding Models
* Hybrid Information Retrieval
* Cross-Encoder Re-ranking
* Website Crawling
* FastAPI Backend Development
* React Frontend Development
* REST API Design

---

# 👨‍💻 Author

**Narran S**

Artificial Intelligence and Data Science Engineering Student

Interested in Artificial Intelligence, Retrieval-Augmented Generation (RAG), Machine Learning, Natural Language Processing, and Full Stack Development.

---

# ⭐ If you found this project helpful, consider giving it a star!
