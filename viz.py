#!/usr/bin/env python3
"""Dorina Nöral Görselleştirici v2 — gerçek hidden state + attention görselleştirme."""
import torch
import asyncio, json
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "C:/dorina-llm/base_model"
ADAPTER = "C:/dorina-llm/model_LoRA"
HOST, PORT = "0.0.0.0", 8001
MAX_NEW = 80
N_NEURONS = 24  # katman başına görselleştirilen nöron sayısı

tok = AutoTokenizer.from_pretrained(BASE)
tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(ADAPTER, device_map="auto",
                                             attn_implementation="eager")
model.eval()
dev = model.device
N_LAYERS = model.config.num_hidden_layers
HIDDEN = model.config.hidden_size
print(f"Model yuklendi. Katman: {N_LAYERS}, hidden: {HIDDEN}. Hazir!", flush=True)


def vram_mb():
    try:
        return round(torch.cuda.memory_allocated() / 1024 / 1024, 1)
    except Exception:
        return 0.0


def ram_mb():
    import psutil
    return round(psutil.Process().memory_info().rss / 1024 / 1024, 1)


def segment_activity(hidden_vec, n=N_NEURONS):
    """Hidden state vektorunu n parçaya bol, her parcanin ortalama |aktivasyonu|."""
    v = hidden_vec.abs()
    total = v.numel()
    size = max(1, total // n)
    acts = []
    for j in range(n):
        seg = v[j * size:(j + 1) * size] if j < n - 1 else v[j * size:]
        acts.append(round(seg.mean().item(), 4) if seg.numel() else 0.0)
    return acts


def normalize(acts):
    mx = max(acts) if acts else 1.0
    return [round(a / mx, 4) if mx > 0 else 0.0 for a in acts]


def vocab_top(logits, k=6):
    probs = torch.softmax(logits.float(), dim=-1).squeeze(0)
    top = torch.topk(probs, k)
    return [(int(i), round(float(p), 4)) for i, p in zip(top.indices, top.values)]


SYSTEM = ("Sen Dorina adinda, Turkce konusan, yardimsever ve zeki bir yapay zeka "
          "asistanisin. Her zaman Turkce cevap ver.")


async def generate_stream(prompt):
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt},
    ]
    enc = tok.apply_chat_template(msgs, tokenize=True, return_dict=True)
    ids = torch.tensor(enc["input_ids"]).unsqueeze(0).to(dev)

    toks_in = [tok.decode([t]) for t in ids[0]]
    yield {"type": "input", "tokens": toks_in, "count": len(toks_in)}

    past = None
    for step in range(MAX_NEW):
        try:
            with torch.no_grad():
                out = model(input_ids=ids, past_key_values=past, use_cache=True,
                            output_hidden_states=True, output_attentions=True)
        except Exception as e:
            import traceback
            yield {"type": "error", "msg": str(e) + "\n" + traceback.format_exc()[-500:]}
            return

        logits = out.logits[0, -1, :]
        past = out.past_key_values
        nxt = int(torch.argmax(logits).item())
        token_str = tok.decode([nxt])
        ids = torch.tensor([[nxt]], device=dev)

        # 28 katman nöron aktivasyonları (embedding haric)
        layers = []
        for h in out.hidden_states[1:]:
            hv = h[0, -1].detach().float().cpu()
            layers.append(normalize(segment_activity(hv)))

        # Attention: son token'in tum gecmise dikkati (katman+head ortalamasi)
        attn = None
        if out.attentions:
            a = torch.stack([at[0] for at in out.attentions])      # (L, H, q, kv)
            a = a.mean(dim=0).mean(dim=0)[-1, :]                   # (kv,) son query
            av = a.detach().float().cpu()
            mx = av.max().item() if av.numel() else 1.0
            attn = [round(float(x) / mx, 4) if mx > 0 else 0.0 for x in av]

        yield {
            "type": "token",
            "token": token_str,
            "idx": nxt,
            "step": step + 1,
            "layers": layers,
            "attn": attn,
            "vram": vram_mb(),
            "ram": ram_mb(),
            "top": vocab_top(logits),
        }
        if nxt == tok.eos_token_id:
            break


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root():
    return open("viz.html", encoding="utf-8").read()


@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            prompt = json.loads(data).get("message", "")
            async for ev in generate_stream(prompt):
                await ws.send_text(json.dumps(ev))
            await ws.send_text(json.dumps({"type": "done"}))
    except Exception:
        pass


if __name__ == "__main__":
    import uvicorn
    print(f"Noral vizualizator v2: http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")