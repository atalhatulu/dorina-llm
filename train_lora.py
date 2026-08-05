#!/usr/bin/env python3
"""Qwen2.5-Instruct + LoRA finetune (CPU). merve verisi ile. trl yeni API."""
import json, os
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from peft import LoraConfig
from trl import SFTTrainer

MODEL = "data/base_model"
OUT_DIR = "output/server"
MAX_SEQ = 512

def main():
    ds = load_dataset("json", data_files={
        "train": "data/turkish_instruct_train.jsonl",
        "validation": "data/turkish_instruct_val.jsonl",
    })
    print("Dataset yüklendi:", ds)
    print("Örnek:", json.dumps(ds["train"]["messages"][0], ensure_ascii=False)[:200])

    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.model_max_length = MAX_SEQ

    model = AutoModelForCausalLM.from_pretrained(MODEL)
    lora = LoraConfig(
        r=16, lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
    )

    args = TrainingArguments(
        output_dir=OUT_DIR,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=4,
        num_train_epochs=2,
        learning_rate=2e-4,
        warmup_steps=20,
        logging_steps=20,
        eval_strategy="steps",
        eval_steps=100,
        save_strategy="epoch",
        save_total_limit=2,
        use_cpu=True,
        dataloader_num_workers=0,
        report_to=[],
    )

    trainer = SFTTrainer(
        model=model,
        args=args,
        train_dataset=ds["train"],
        eval_dataset=ds["validation"],
        processing_class=tok,
        peft_config=lora,
    )
    trainer.train()
    trainer.save_model("data/model_LoRA")
    tok.save_pretrained("data/model_LoRA")
    print("=== EĞİTİM BİTTİ ===")
    print("Model: data/model_LoRA")

if __name__ == "__main__":
    main()
