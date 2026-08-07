#!/usr/bin/env python3
"""Türkçe LLM web arayüzü — FastAPI sunucusu (RTX 4050 laptop)."""
import torch
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from transformers import AutoModelForCausalLM, AutoTokenizer
import json, os

BASE = "C:/dorina-llm/base_model"
ADAPTER = "C:/dorina-llm/model_LoRA"
HOST = "0.0.0.0"
PORT = 8000

# Modeli bir kez yükle
print("Yükleniyor...", flush=True)
tok = AutoTokenizer.from_pretrained(BASE)
tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(ADAPTER, device_map="auto")
print("Model yüklendi. Hazır!", flush=True)

app = FastAPI()

HTML = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dorina 1.5B</title>
<style>
  body { background:#131418; color:#e8e8e8; font-family:'Segoe UI',sans-serif; margin:0; height:100vh; display:flex; flex-direction:column; }
  header { padding:16px 24px; background:#1b1c22; border-bottom:1px solid #2a2b33; display:flex; align-items:center; gap:12px; }
  header h1 { margin:0; font-size:18px; color:#fff; }
  header span { font-size:12px; color:#6dc8ff; background:#0f2431; padding:4px 10px; border-radius:20px; }
  #chat { flex:1; overflow-y:auto; padding:24px; display:flex; flex-direction:column; gap:14px; }
  .msg { max-width:75%; padding:12px 16px; border-radius:14px; line-height:1.5; white-space:pre-wrap; font-size:15px; }
  .user { align-self:flex-end; background:#2d3553; border-bottom-right-radius:4px; }
  .bot { align-self:flex-start; background:#22242b; border:1px solid #2f313a; border-bottom-left-radius:4px; }
  .bot.loading::after{ content:' ▍'; animation:blink 1s infinite; }
  @keyframes blink{ 0%{opacity:0} 50%{opacity:1} 100%{opacity:0} }
  #bar { display:flex; gap:10px; padding:14px 24px; background:#1c1c22; border-top:1px solid #2a2b33; }
  #input { flex:1; background:#22242b; border:1px solid #33353f; color:#e8e8e8; padding:12px 16px; border-radius:10px; font-size:15px; outline:none; }
  #input:focus { border-color:#6dc8a0; }
  #send { background:#3a7d5f; border:none; color:#fff; padding:12px 22px; border-radius:10px; cursor:pointer; font-size:15px; font-weight:600; }
  #send:hover{ background:#478f6d; }
  #status { font-size:12px; color:#888; padding:2px 24px; }
</style>
</head>
<body>
<header>
  <div class="logo">🧠 Dorina</div>
  <span>Dorina 1.5B · Türkçe · RTX 4050</span>
</header>
<div id="chat"></div>
<div id="status">Model hazır.</div>
<div id="bar">
  <input id="input" placeholder="Bir şey sor..." autocomplete="off" />
  <button id="send">Gönder</button>
</div>
<script>
const chat = document.getElementById('chat');
const input = document.getElementById('input');
const send = document.getElementById('send');
const status = document.getElementById('status');

function add(role, text) {
  const d = document.createElement('div');
  d.className = 'msg ' + role;
  d.textContent = text;
  chat.appendChild(d);
  chat.scrollTop = chat.scrollHeight;
  return d;
}

async function generate(text) {
  status.textContent = 'Düşünüyor... (CPU/GPU)';
  const loading = add('ai', '');
  loading.classList.add('loading');
  const res = await fetch('/chat', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({message:text})
  });
  const data = await res.json();
  loading.classList.remove('loading');
  loading.textContent = data.reply;
  status.textContent = 'Model hazır.';
  chat.scrollTop = chat.scrollHeight;
}

send.addEventListener('click', () => {
  const t = input.value.trim();
  if (!t) return;
  add('user', t);
  input.value = '';
  generate(t);
});
input.addEventListener('keydown', e => { if (e.key === 'Enter') send.click(); });
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML

@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    msg = body.get("message", "")
    msgs = [{"role": "user", "content": msg}]
    enc = tok.apply_chat_template(msgs, return_tensors="pt", return_dict=True)
    ids = enc["input_ids"].to(model.device)
    out = model.generate(
        ids, max_new_tokens=200, do_sample=True,
        temperature=0.7, top_p=0.9,
        pad_token_id=tok.eos_token_id,
    )
    reply = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
    return {"reply": reply.strip()}

if __name__ == "__main__":
    import uvicorn
    print(f"Sunucu: http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")