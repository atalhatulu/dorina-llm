#!/usr/bin/env python3
"""Eğitilmiş LoRA modelini test et."""
import sys
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "data/base_model"
ADAPTER = "data/model_LoRA"

def main():
    if len(sys.argv) > 1:
        soru = " ".join(sys.argv[1:])
    else:
        soru = "Türkiye'nin başkenti neresidir?"

    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForCausalLM.from_pretrained(ADAPTER)
    msgs = [{"role": "user", "content": soru}]
    enc = tok.apply_chat_template(msgs, return_tensors="pt", return_dict=True)
    ids = enc["input_ids"]
    out = model.generate(ids, max_new_tokens=150, do_sample=True, temperature=0.7)
    cevap = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
    print(f"SORU: {soru}\nCEVAP: {cevap}")

if __name__ == "__main__":
    main()
