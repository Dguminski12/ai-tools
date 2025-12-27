# 🧠 ~AI Tools API

A secure, FastAPI-powered backend for interacting with your local development environment — safely.  
It exposes controlled endpoints for listing, reading, searching, writing, and appending files inside a sandboxed directory (`DEV_ROOT`).

---

## 🚀 Features

- 🔍 **Search** within your dev workspace for code or text patterns  
- 📂 **List directories** and inspect project structure  
- 📖 **Read files** with line-range control  
- ✏️ **Write / Append** text files safely  
- 🔐 **Protected with API key authentication**  
- 🧱 **Sandboxed to `DEV_ROOT`**, preventing access outside allowed scope  
- 🧰 Designed for **AI-assisted developer tools** or Pi-based automation  

---

## ⚙️ Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)  
- [Uvicorn](https://www.uvicorn.org/)  
- Python 3.10+  
- Pydantic for request validation  

---

## 🗂️ Project Structure

```
~ai-tools/
├── server.py          # Main FastAPI backend
├── openai.yaml        # Optional config for API integration
├── README.md          # You are here
└── __pycache__/       # Cache (ignored)
```

---

## 🧾 API Overview

### 🔑 Authentication

All routes (except `/health`) require a valid API key header:

```
x-api-key: <your_api_key>
```

Your key is read from the environment variable:

```bash
export PI_TOOLS_API_KEY="your-secret-key"
```

---

### 📡 Endpoints

| Method | Endpoint     | Description |
|--------|---------------|-------------|
| `GET`  | `/health`     | Check server status |
| `GET`  | `/list?path=` | List directory contents under `DEV_ROOT` |
| `POST` | `/read`       | Read a file by path and line range |
| `POST` | `/search`     | Search for text within workspace files |
| `POST` | `/write`      | Create or overwrite a file |
| `POST` | `/append`     | Append content to a file |

---

### Example: Reading a File

```bash
curl -X POST http://localhost:5050/read \
  -H "x-api-key: $PI_TOOLS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"path": "python-labs/example.py", "start_line": 1, "end_line": 100}'
```

---

## 🧰 Development

### Run locally

```bash
pip install fastapi uvicorn pydantic
uvicorn server:app --host 0.0.0.0 --port 5050 --reload
```

or use the built-in runner:

```bash
python server.py
```

---

## 🧿 Security Notes

- Access is **restricted** to the `DEV_ROOT` path (`/home/d-guminski/dev`).  
- Denies access to `.env`, `.ssh`, secret keys, and binary certificate files.  
- Files larger than 200KB are rejected for safety.  

---

## 📄 License

MIT © 2025 — Designed for private Pi-based AI development tools.

---

## 💡 Future Ideas

- Add support for **file diffs / patches**
- Integrate **OpenAI function calling**
- Expose **AI command interface** for file editing
- Optional **read-only mode**

---

## 🧩 Maintainer

**@d-guminski**  
Built for Raspberry Pi Dev Environment