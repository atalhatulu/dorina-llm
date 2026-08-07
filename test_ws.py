import json
from websockets.sync.client import connect

ws = connect("ws://127.0.0.1:8001/ws")
ws.send(json.dumps({"message": "Merhaba, 2 arti 3 kac eder?"}))
n = 0
try:
    while True:
        m = json.loads(ws.recv(timeout=15))
        if m["type"] == "input":
            print("GIRDI token sayisi:", m["count"], "| ilk 5:", m["tokens"][:5])
        elif m["type"] == "token":
            n += 1
            if n <= 12:
                l0 = m["layers"][0]
                l27 = m["layers"][27]
                print(f"  [tok {n}] '{m['token']}' | L0={l0} L27={l27} | VRAM={m['vram']}MB | top1={m['top'][0][0]}")
        elif m["type"] == "done":
            print("BITTI. toplam token:", n)
            break
except Exception as e:
    print("bitti/hata:", type(e).__name__)
ws.close()