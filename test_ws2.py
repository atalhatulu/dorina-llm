import json
from websockets.sync.client import connect

ws = connect("ws://127.0.0.1:8001/ws")
ws.send(json.dumps({"message": "Merhaba, kendini tanitir misin?"}))
n = 0
try:
    while True:
        m = json.loads(ws.recv(timeout=20))
        if m["type"] == "input":
            print("GIRDI:", m["count"], "token. Ilk 6:", [t.replace(chr(10),'').strip() for t in m["tokens"][:6]])
        elif m["type"] == "token":
            n += 1
            if n <= 10:
                l0 = m["layers"][0][:4]
                l27 = m["layers"][27][:4]
                attn_len = len(m["attn"]) if m.get("attn") else 0
                print(f"  tok{n}='{m['token']}' | L0={l0} L27={l27} | attn_len={attn_len} | VRAM={m['vram']}MB RAM={m['ram']}MB | güv={m['top'][0][1]}")
        elif m["type"] == "error":
            print("SUNUCU HATASI:", m["msg"][:200]); break
        elif m["type"] == "done":
            print("BITTI. toplam token:", n); break
except Exception as e:
    print("baglanti kapandi:", type(e).__name__, "| token sayisi:", n)
ws.close()