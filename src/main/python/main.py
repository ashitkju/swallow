import json
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA

app = FastAPI(title="Codebase QA Bot")

# ─── Load & Chunk ──────────────────────────────────────────────────────────────
def load_and_chunk(json_path: str):
    # 1. Read the JSON produced by your Java parser
    data = json.loads(Path(json_path).read_text())

    # 2. Build a Document per class
    docs = []
    for entry in data:
        class_name = entry["className"]
        file_path  = entry["filePath"]
        methods    = [m["methodName"] for m in entry.get("methods", [])]
        comments   = entry.get("comments", [])

        # Compose a single text blob
        content = "\n".join([
            f"Class: {class_name}",
            f"File: {file_path}",
            "Methods:",
            *[f"  - {m}" for m in methods],
            "Comments:",
            *[f"  - {c}" for c in comments],
        ])

        docs.append(Document(
            page_content=content,
            metadata={
                "class": class_name,
                "file_path": file_path
            }
        ))

    # 3. Split into chunks (so long classes don’t blow past token limits)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)
    return chunks

# Preload at startup
CHUNKS = load_and_chunk("code_metadata.json")
print(f"✅ Loaded and split into {len(CHUNKS)} chunks.")

# ─── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/ping")
def ping():
    return {"message": "FastAPI is alive!"}

@app.get("/chunks")
def get_chunks():
    # Returns an overview of your chunks (for sanity-check)
    overview = [
        {"metadata": c.metadata, "snippet": c.page_content[:100] + "..."}
        for c in CHUNKS
    ]
    return JSONResponse(overview)

# ─── Setup RAG Engine ─────────────────────────────────────────────────────────

def setup_rag(chunks):
    print("⏳ Creating embeddings via Ollama...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")  # or "llama3", "mxbai", etc.

    # db = FAISS.from_documents(chunks, embedding=embeddings)
    # print("⏳ Saving vector store to DB...")
    # db.save_local("code_vector_db")
    db = FAISS.load_local("code_vector_db", embeddings, allow_dangerous_deserialization=True)

    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    print("⏳ Starting Ollama LLM...")
    llm = OllamaLLM(model="llama3")  # you can change to "mistral", "codellama", etc.

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    print("✅ QA chain ready.")
    return qa_chain

QA_CHAIN = setup_rag(CHUNKS)


@app.get("/ask")
def ask_question(q: str = Query(..., description="Your dev question about the code")):
    try:
        result = QA_CHAIN(q)
        return {
            "question": q,
            "answer": result["result"],
            "sources": [doc.metadata for doc in result["source_documents"]]
        }
    except Exception as e:
        return {"error": str(e)}