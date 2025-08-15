# 📄 RAG Pipeline – Document Question-Answering API

Upload documents (PDF / DOCX / TXT), ask questions, and get **cited answers**.  
Built with **FastAPI**, **Sentence-Transformers**, **FAISS**, and **Docker**.

---

## 1 🚀 Setup & Installation

### 1.1 Prerequisites
- Python **3.11+**
- Git *(optional)*
- Docker & Docker Compose **v2+** *(optional)*

---

### 1.2 Local Installation
```bash
git clone https://github.com/<YOUR_USERNAME>/rag-pipeline-assignment.git
cd rag-pipeline-assignment
pip install -r app/requirements.txt
python app/main.py
# API → http://localhost:8000/docs
```

---

### 1.3 Docker Usage
```bash
docker compose build    # first build ≈ 15 min
docker compose up
# API → http://localhost:8000/docs
```

---

## 2 📋 API Usage & Testing

| Method | Path       | Purpose                                                |
|--------|-----------|--------------------------------------------------------|
| **POST** | `/upload`   | Upload ≤ 20 docs (≤ 10 MB each, ≤ 1000 pages)          |
| **POST** | `/query`    | Ask a question over uploaded docs                     |
| **GET**  | `/metadata` | List stored docs & chunk counts                       |
| **GET**  | `/health`   | Service health-check                                  |

---

### Example Workflow

**📤 Upload**
```bash
curl -F "files=@sample.pdf" http://localhost:8000/upload
```

**❓ Query**
```bash
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query":"What is football?","top_k":3}'
```

**📊 Check metadata / health**
```bash
curl http://localhost:8000/metadata
curl http://localhost:8000/health
```

---

## 3 ⚙️ Configuring Different LLM Providers

### 3.1 Current Defaults
- **Embedding model**: `all-MiniLM-L6-v2` (Sentence-Transformers)
- **Answer generator**: Simple extractive method

---

### 3.2 🔄 Switch Embedding Model
Edit `app/utils.py` (`DocumentProcessor.init`):
```python
self.embedding_model = SentenceTransformer("intfloat/e5-base-v2")
```

---

### 3.3 🤖 Integrate OpenAI (Generative Answers)

**Install & set API key**
```bash
pip install openai
export OPENAI_API_KEY=sk-...
```

**Edit** `generate_response` in `app/utils.py`:
```python
from openai import OpenAI
client = OpenAI()

async def generate_response(self, query, chunks):
    context = "\n\n".join(c["text"] for c in chunks[:5])
    prompt = f"Answer based only on this context:\n{context}\n\nQ: {query}\nA:"
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.1
    )
    return r.choices[0].message.content
```

---

### 3.4 🌐 Other Providers

| Provider      | Install                  | Env Vars                                          |
|---------------|--------------------------|---------------------------------------------------|
| Azure OpenAI  | `pip install openai`     | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`   |
| Cohere        | `pip install cohere`     | `COHERE_API_KEY`                                  |
| HF Inference  | `pip install huggingface_hub` | `HUGGINGFACEHUB_API_TOKEN`                   |

Replace the OpenAI call with the provider’s SDK; retrieval (FAISS) stays unchanged.

---

### 3.5 📝 `.env` Example
```env
OPENAI_API_KEY=sk-...
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
COHERE_API_KEY=
ENVIRONMENT=production
HF_ENDPOINT=https://hf-mirror.com
```

---

## 4 🏗 Project Structure
```
rag-pipeline/
├─ app/
│  ├─ main.py        # FastAPI entry
│  ├─ utils.py       # DocumentProcessor & VectorStore
│  ├─ models.py      # Pydantic schemas
│  ├─ database.py    # Metadata store
│  └─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ .dockerignore
└─ README.md
```

---

## 5 🧪 Development & Testing
```bash
pip install pytest pytest-asyncio httpx
pytest tests/
```

**💡 Optimization tips**:
- Use `.dockerignore`
- Cache Python dependencies
- Consider **GPU embedding** for speed

---

## 6 🤝 Contributing / Support
Open issues or PRs on [GitHub](https://github.com/<YOUR_USERNAME>/rag-pipeline-assignment) – all contributions welcome!

---

© 2025 **RAG Pipeline Project**
