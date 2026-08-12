# dorina-llm

Türkçe LLM (Qwen2.5-Instruct) LoRA/QLoRA ince ayar (finetune) projesi — `trl` / `PEFT` / `transformers` ile.

Dorina Agent için Türkçe bir model geliştirmek amacıyla hazırlanmış uçtan uca eğitim hattı (pipeline): veri hazırlama → LoRA/QLoRA eğitimi → FastAPI web arayüzü ve nöral görselleştirici. `PLAN.md` içindeki karar ile CPU ve CUDA (RTX 4050) olmak üzere iki donanım yoluna ayrılır.

## Özellikler

- **Veri hazırlama (`prepare_data.py`)** — `merve/turkish_instructions` CSV'sini chat (`messages`) formatına çevirir, "talimat/giriş/çıktı" alanlarını birleştirir, `data/` altına train/val (90/10) JSONL dağıtır
- **Train/val verisi (`data/`)** — hazır `turkish_instruct_train.jsonl` (~2.2MB) ve `turkish_instruct_val.jsonl` (~227KB)
- **CPU eğitimi (`train_lora.py`)** — LoRA (`r=16, alpha=32`, `q/k/v/o/gate/up/down_proj`), gradient accumulation 4, `use_cpu=True`, `SFTTrainer`; çıktı `data/model_LoRA`
- **CUDA/QLoRA eğitimi (`train_laptop.py`)** — RTX 4050 için 4-bit `BitsAndBytes` (nf4 + double quant, bf16), QLoRA; çıktı `C:/dorina-llm/model_LoRA`
- **LLM web arayüzü (`server.py`)** — FastAPI + StreamingResponse, `data/model_LoRA` adapter'ını `data/base_model` taban modeliyle birlikte yükleyen sohbet UI (localhost:8000)
- **Nöral görselleştirici (`viz.py` + `viz.html`)** — WebSocket tabanlı, katman başına gerçek hidden state + attention parça aktivasyonu görselleştirme (localhost:8001)
- **Test scriptleri** — `test_generate.py` (token akışı), `test_model.py`, `test_ws.py`/`test_ws2.py` (WebSocket)
- **Windows otomasyon scriptleri** — `run_*.ps1`, `start_*.ps1` (server/train/viz/webui/watchdog), `download_model.ps1` vb.

## Dizin Yapısı

```
dorina-llm/
├── PLAN.md                 # Eğitim planı & donanım karar notları
├── prepare_data.py         # CSV → JSONL chat formatı dönüştürücü
├── train_lora.py           # CPU LoRA finetune
├── train_laptop.py         # CUDA QLoRA finetune (RTX 4050)
├── server.py               # FastAPI sohbet arayüzü
├── viz.py / viz.html       # Nöral görselleştirici (WebSocket)
├── test_*.py               # Model / WebSocket testleri
├── data/
│   ├── turkish_instruct_train.jsonl
│   └── turkish_instruct_val.jsonl
└── *.ps1                   # Windows otomasyon scriptleri
```

## Kurulum

Python 3.11/3.12 sanal ortamı önerilir (ML kütüphaneleri 3.14'ü tam desteklemeyebilir). CPU eğitimi için:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers datasets peft trl bitsandbytes
```

CUDA (RTX 4050) için standart `torch` CUDA wheels'i kullanılır.

## Kullanım

### Veriyi hazırla

```bash
python prepare_data.py   # SRC'yi (/tmp/tr_instructions.csv) chat formatına çevirir
```

### CPU ile LoRA eğitimi

```bash
python train_lora.py     # data/model_LoRA'ya kaydeder
```

### CUDA ile QLoRA eğitimi (laptop)

```bash
python train_laptop.py   # C:/dorina-llm/model_LoRA'ya kaydeder
```

### Web arayüzü / görselleştirici

```bash
python server.py   # http://localhost:8000  (sohbet)
python viz.py      # http://localhost:8001  (nöral görselleştirme)
```

Not: `server.py` ve `viz.py` içindeki `BASE` / `ADAPTER` / veri dosyası yolları Windows dizinlerine (`C:/dorina-llm/...`) sabitlenmiş olup kendi ortamına göre güncellenmelidir.

## Gereksinimler

- Python 3.11/3.12
- PyTorch, `transformers`, `datasets`, `peft`, `trl`, `bitsandbytes` (CPU'da LPU/8-bit yerine fp32 LoRA önerilir)
- Eğitim sonrası GGUF'a çevirip çalıştırmak için `llama.cpp` (opsiyonel, Q4_K_M quantization)
- CUDA eğitimi için RTX 4050 sınıfı (bf16 destekli) NVIDIA GPU
