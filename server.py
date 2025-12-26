from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from pathlib import Path
import os
import re

app = FastAPI(title="Pi Dev Tools", version="1.0.0")

# development root directory
DEV_ROOT = Path("/home/d-guminski/dev").resolve()

# API key
def get_api_key():
    return os.environ.get("PI_TOOLS_API_KEY", "")


# Block obvious secret locations / patterns
DENY_DIRS = {"~/.ssh", "/etc", "/var/lib", "/var/log"}
DENY_FILENAMES = {".env", ".env.local", "id_rsa", "id_ed25519"}
DENY_EXTS = {".key", ".pem", ".p12", ".pfx"}

MAX_READ_BYTES = 200_000  # 200KB per read (keeps Pi + tokens sane)
MAX_RESULTS = 50

def require_key(x_api_key: str | None = Header(default=None)):
    api_key = get_api_key()

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Server missing PI_TOOLS_API_KEY"
        )

    if x_api_key != api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )


def safe_resolve(rel_path: str) -> Path:
    # Normalize and resolve within DEV_ROOT
    p = (DEV_ROOT / rel_path).resolve()
    if not str(p).startswith(str(DEV_ROOT)):
        raise HTTPException(status_code=400, detail="Path escapes DEV_ROOT")
    # Deny certain dirs
    for d in DENY_DIRS:
        if str(p).startswith(str(Path(d).expanduser().resolve())):
            raise HTTPException(status_code=403, detail="Path not allowed")
    # Deny secret-like names/ext
    if p.name in DENY_FILENAMES or p.suffix.lower() in DENY_EXTS:
        raise HTTPException(status_code=403, detail="File not allowed")
    return p

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/list")
def list_dir(path: str = "", x_api_key: str | None = Header(default=None)):
    require_key(x_api_key)
    p = safe_resolve(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Not found")
    if p.is_file():
        return {"path": str(p.relative_to(DEV_ROOT)), "type": "file"}
    items = []
    for child in sorted(p.iterdir()):
        if child.name.startswith("."):
            continue
        items.append({
            "name": child.name,
            "type": "dir" if child.is_dir() else "file",
        })
    return {"path": str(p.relative_to(DEV_ROOT)), "items": items[:500]}

class ReadBody(BaseModel):
    path: str
    start_line: int = 1
    end_line: int = 200

@app.post("/read")
def read_file(body: ReadBody, x_api_key: str | None = Header(default=None)):
    require_key(x_api_key)
    p = safe_resolve(body.path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    size = p.stat().st_size
    if size > MAX_READ_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large ({size} bytes). Use smaller file or narrow.")
    lines = p.read_text(errors="replace").splitlines()
    s = max(1, body.start_line)
    e = min(len(lines), body.end_line)
    chunk = lines[s-1:e]
    return {
        "path": str(p.relative_to(DEV_ROOT)),
        "start_line": s,
        "end_line": e,
        "total_lines": len(lines),
        "content": "\n".join(chunk),
    }

class SearchBody(BaseModel):
    query: str
    max_results: int = 20

@app.post("/search")
def search(body: SearchBody, x_api_key: str | None = Header(default=None)):
    require_key(x_api_key)
    q = body.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Empty query")

    max_results = min(MAX_RESULTS, max(1, body.max_results))

    results = []
    pattern = re.compile(re.escape(q), re.IGNORECASE)

    # Walk DEV_ROOT but skip dot dirs
    for root, dirs, files in os.walk(DEV_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in files:
            if fn.startswith("."):
                continue
            if fn in DENY_FILENAMES:
                continue
            p = Path(root) / fn
            if p.suffix.lower() in DENY_EXTS:
                continue
            try:
                if p.stat().st_size > MAX_READ_BYTES:
                    continue
                text = p.read_text(errors="replace")
            except Exception:
                continue

            for i, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    results.append({
                        "path": str(p.relative_to(DEV_ROOT)),
                        "line": i,
                        "match": line[:300],
                    })
                    if len(results) >= max_results:
                        return {"query": q, "results": results}
    return {"query": q, "results": results}
