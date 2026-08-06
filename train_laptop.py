#!/usr/bin/env python3
"""Qwen2.5-1.5B-Instruct + QLoRA finetune (RTX 4050, CUDA)."""
import json, os
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, BitsAndBytesConfig
from peft import LoraConfig, prepare_model_for_kbit_training
from trl import SFTTrainer

MODEL = "C:/dorina-llm/base_model"
OUT_DIR = "C:/dorina-llm/output"
MAX_SEQ = 1024

def main():
    ds = load_dataset("json", data_files={
        "train": "C:/dorina-llm/turkish_instruct_train.jsonl",
        "validation": "C:/dorina-llm/turkish_instruct_val.jsonl",
    })
    print("Dataset:", ds)
    print("CUDA:", torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else "YOK")

    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.model_max_length = MAX_SEQ

    # QLoRA: 4-bit quantize (bf16 compute — 4050 Ada bf16 destekler, scaler gerekmez)
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, quantization_config=bnb, device_map="auto",
        torch_dtype=torch.bfloat16,
    )
    model = prepare_model_for_kbit_training(model)

    lora = LoraConfig(
        r=16, lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
    )

    args = TrainingArguments(
        output_dir=OUT_DIR,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=4,
        num_train_epochs=2,
        learning_rate=2e-4,
        warmup_steps=20,
        logging_steps=20,
        eval_strategy="steps",
        eval_steps=100,
        save_strategy="epoch",
        save_total_limit=2,
        fp16=False,
        bf16=True,
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
    trainer.save_model("C:/dorina-llm/model_LoRA")
    tok.save_pretrained("C:/dorina-llm/model_LoRA")
    print("=== EĞİTİM BİTTİ ===")

if __name__ == "__main__":
    main()
