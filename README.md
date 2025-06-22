# swallow
A LLM chatbot helps to understand and navigate an unknown/new codebase.

# 🧠 Codebase QA Bot – Setup Instructions

This guide helps you set up a hybrid **Spring Boot + Python + Ollama** codebase assistant that can answer questions about your Java project.

---

## ✅ 1. Generate Metadata from Java Code

Run your **Spring Boot project** to generate the `code_metadata.json` file.  
This file should contain class, method, and comment metadata extracted from your Java codebase.

---

## 📦 2. Install Python Dependencies

First, upgrade `pip` if needed:

```bash
python -m pip install --upgrade pip
```

Then install all required packages from req.txt file provided along with source code:

```bash
pip install -r req.txt
```

---

## 🤖 3. Run Ollama & Load the LLM

Ensure [Ollama](https://ollama.com) is installed.

Start the desired language model (e.g. `llama3`) using:

```bash
ollama run llama3
```

> 💡 You can also try other models like `mistral`, `codellama`, or `deepseek`.

---

## 🚀 4. Launch the Python FastAPI App

Start the API server with:

```bash
uvicorn main:app --reload
```

This will start your local server at `http://localhost:8000`.

---

## ⏱️ 5. Embedding Time (One-Time)

Embedding your codebase may take time depending on chunk size and system specs.

> On a Ryzen 7 + GTX 1660 Ti + 16GB RAM system:  
> 🕒 **~30 minutes** to embed ~20,000 chunks

This is a **one-time operation** if you persist your FAISS vector store.

---

## 🌐 6. Ask Questions About Your Codebase

Use this endpoint to query your codebase via LLM:

```
http://localhost:8000/ask?q=AskAnything?
```

This leverages **retrieval-augmented generation (RAG)** using your actual source code — no LLM hallucinations.

---

Happy coding! 💻