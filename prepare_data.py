#!/usr/bin/env python3
"""merve/turkish_instructions CSV -> chat format (messages) -> train/val split."""
import csv, json, random, sys

SRC = "/tmp/tr_instructions.csv"
OUT = "data/turkish_instruct"
N_SAMPLES = 5000
VAL_RATIO = 0.1
SEED = 42

def main():
    random.seed(SEED)
    rows = []
    with open(SRC, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [fn.strip() if fn else fn for fn in reader.fieldnames]
        for r in reader:
            talimat = (r.get("talimat") or "").strip()
            giris = (r.get("giriş") or "").strip()
            cikti = (r.get("çıktı") or "").strip()
            if not talimat or not cikti:
                continue
            if giris and giris.lower() not in ("nan", "none"):
                user = f"{talimat}\n\nBağlam: {giris}"
            else:
                user = talimat
            rows.append({
                "messages": [
                    {"role": "user", "content": user},
                    {"role": "assistant", "content": cikti},
                ]
            })

    print(f"Toplam geçerli örnek: {len(rows)}")
    random.shuffle(rows)
    if len(rows) > N_SAMPLES:
        rows = rows[:N_SAMPLES]
    n_val = int(len(rows) * VAL_RATIO)
    train, val = rows[n_val:], rows[:n_val]
    print(f"train: {len(train)}, val: {len(val)}")

    import os
    os.makedirs("data", exist_ok=True)
    with open(f"{OUT}_train.jsonl", "w", encoding="utf-8") as f:
        for r in train:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(f"{OUT}_val.jsonl", "w", encoding="utf-8") as f:
        for r in val:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Yazıldı: {OUT}_train.jsonl, {OUT}_val.jsonl")

if __name__ == "__main__":
    main()
