#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export OLLAMA_HOST="127.0.0.1:11434"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🧠  RAG System — Enterprise Console"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Start Ollama server in background ────────────────────────────────────────
if curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "  ✅  Ollama already running"
else
    echo "  ⏳  Starting Ollama server…"
    ollama serve &
    OLLAMA_PID=$!
    for i in $(seq 1 30); do
        if curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
            echo "  ✅  Ollama ready"
            break
        fi
        sleep 1
    done
fi

# ── Pull required models in background (non-blocking) ────────────────────────
echo "  📥  Pulling models in background (first run may take a while)…"
(ollama pull llama3.2 && echo "  ✅  llama3.2 ready") &
(ollama pull nomic-embed-text && echo "  ✅  nomic-embed-text ready") &

# ── Ensure data directories exist ────────────────────────────────────────────
mkdir -p data

# ── Start Streamlit ───────────────────────────────────────────────────────────
echo "  🌐  Starting Streamlit on port 8080…"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
exec streamlit run app.py \
    --server.port 8000 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false
