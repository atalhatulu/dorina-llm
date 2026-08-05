# dorina-llm — Kendi LLM'ini Eğitme Planı

Tarih: 2026-08-05
Mevcut donanım: RX 5500 XT (RDNA1, 4GB VRAM), 15GB RAM, ~38GB boş disk, ROCm yok.

---

## 0. ÖNEMLİ GERÇEK (kritik)

**Sıfırdan (pretrain) LLM eğitmek bu donanımda mantıksız.**
- 4GB VRAM + 15GB RAM ile sıfırdan eğitim = günler/haftalar sürer, sonuç düşük kalite.
- RDNA1 (RX 5000 serisi) modern ROCm'de DESTEKLENMİYOR. GPU eğitimi pratikte kapalı.
- Çözüm yolu: **hazır temel model al + LoRA/QLoRA ile finetune et** (ince ayar). Bu hem bu donanımda yapılabilir hem de gerçek iş görür.

**2 yol var:**
| Yol | Ne yapar | Bu donanımda |
|---|---|---|
| A) Pretrain (sıfırdan) | Dev veriyle dil öğrenir | ❌ imkansıza yakın |
| B) Finetune (LoRA/QLoRA) | Hazır modele uzmanlık kazandırır | ✅ yapılabilir |

---

## 1. HEDEF NETLEŞTİRME (önce bunu konuşalım)

Finetune bile önce şu sorulara cevap ister:
1. **Model ne yapacak?** (Türkçe asistan? Kod yazma? Sohbet? Dorina'ya entegre olacak mı?)
2. **Hangi temel model?** Öneriler:
   - Qwen2.5-1.5B-Instruct — küçük, Türkçesi fena değil, LoRA ile iyi çalışır
   - Gemma-2-2B — kaliteli ama biraz ağır
   - Qwen2.5-0.5B — çok küçük, hızlı deneme için
   - Llama-3.2-1B / 3B — iyi ama Türkçe zayıf
3. **Veri nereden?** (Kendi verin mi var, yoksa sentetik üretecek miyiz?)
4. **Ne kadar süre/token bütçesi var?**

Öneri: **Qwen2.5-1.5B-Instruct + QLoRA** başlangıç noktası.

---

## 2. ADIM ADIM PLAN

### ADIM 0: Ortam kurulumu
- Python 3.14 var; ML kütüphaneleri 3.14'ü TAM desteklemiyor olabilir → **Python 3.11/3.12 sanal ortamı şart** (uv veya conda).
- CPU eğitimi: `pip install torch --index-url https://download.pytorch.org/whl/cpu`
- Kütüphaneler: `transformers`, `datasets`, `peft`, `trl`, `bitsandbytes` (CPU'da bitsandbytes sorunlu olabilir → 4-bit yerine 8-bit ya da normal fp32 küçük model).
- Alternatif CPU-yerli: **mlx** (Apple) değil, Linux CPU için **llama.cpp + llama-finetune** veya **unsloth** (CPU destekli mi kontrol et).

### ADIM 1: Veri toplama/hazırlama
Format (chat template):
```
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```
- Kendi verin yoksa: HuggingFace'te Türkçe instruct veri setleri (örn. Turkcell/Atlas, büyük Türkçe corpora).
- Sentetik veri: büyük bir modelle (OmniRoute/free API) soru-cevap üret.
- Veri kalitesi > miktar. 10.000 temiz örnek, 1M kirli örnekten iyidir.

### ADIM 2: Veriyi tokenize et
- Modelin tokenizer'ı ile işle.
- `max_seq_length` = 1024-2048 (15GB RAM'de 2048 zorlanabilir, 1024 güvenli başlangıç).
- Eğitim/validation split: 90/10.

### ADIM 3: LoRA/QLoRA ile eğitim
- PEFT ile LoRA: `r=16, alpha=32, target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"]`
- QLoRA (4-bit) CPU'da zor → **CPU'da normal LoRA fp32/bf16** daha pratik.
- Batch: gradient_accumulation ile küçük batch (1-2) + accumulation 4-8.
- Optimizer: AdamW, lr=2e-4 (LoRA için), warmup.
- Epoch: 2-3. Overfit'e dikkat, validation loss izle.

### ADIM 4: Değerlendirme
- Eğitim sonrası aynı soruları eğitim öncesiyle karşılaştır.
- Rastgele 20-50 test sorusu, insan gözüyle puanla.
- Perplexity/accuracy metrikleri yanıltıcı olabilir; manuel değerlendirme şart.

### ADIM 5: Export + kullanım
- LoRA adapter'ını temel modele merge et.
- GGUF'a çevir (llama.cpp ile) → 4GB VRAM'de quantize (Q4_K_M) çalıştır.
- Dorina'ya entegrasyon: ollama veya llama.cpp server + OpenAI uyumlu API.

---

## 3. ZAMAN & KAYNAK TAHMİNİ (CPU'da, 15GB RAM)

| Model | Veri | Eğitim süresi (tahmini) |
|---|---|---|
| Qwen2.5-0.5B | 5K örnek | 1-3 saat |
| Qwen2.5-1.5B | 10K örnek | 4-10 saat |
| Qwen2.5-1.5B | 50K örnek | 1-2 gün |

(CPU'da token/saniye düşük; gerçek hızı ölçüp planı güncelleriz.)

---

## 4. ARAŞTIRMA NOTLARI (daha derin okuma için)

- **LoRA**: Low-Rank Adaptation — full fine-tune'a göre ~100x daha az parametre günceller. GPU'da 4GB VRAM'e QLoRA ile 7B bile sığar; CPU'da küçük modellerde düz LoRA.
- **QLoRA**: 4-bit quantize + LoRA. NVIDIA'da bitsandbytes ile; AMD/CPU'da sınırlı destek.
- **unsloth**: 2x hızlı LoRA eğitimi, CPU/AMD desteği kısıtlı olabilir — önce dene, olmazsa klasik transformers.
- **TRL (Transformer Reinforcement Learning)**: SFTTrainer ile en kolay başlangıç.
- **Veri seti önerileri**:
  - HuggingFace: `teknium/OpenHermes-2.5` (EN), Türkçe için `ozgur-yilmaz` / `TurKLoRA` gibi Türkçe LoRA repoları
  - Kendi Dorina sohbet geçmişi (SQLite'ı var!) → en değerli veri kaynağı. Dorina'nın session_fts verisi finetune verisi olabilir!
- **GGUF**: llama.cpp formatı, 4GB VRAM'de Q4_K_M quantize ile 1.5B model rahat çalışır.

---

## 5. ÖNERİLEN İLK ADIM (MVP)

1. Python 3.11/3.12 venv kur (uv ile: `uv venv --python 3.11`)
2. `pip install transformers datasets peft trl accelerate`
3. HuggingFace'ten Qwen2.5-0.5B-Instruct indir
4. Küçük Türkçe veri seti bul (2-5K örnek)
5. TRL SFTTrainer + LoRA ile eğit
6. Sonucu GGUF'a çevir, llama.cpp ile test et

Bu MVP 1 günde biter, pipeline'ı doğrular, sonra 1.5B'ye geçeriz.

---

## 6. AÇIK SORULAR (bunlara cevap ver, plan netleşsin)

1. Model ne yapsın? (asistan / kod / sohbet / başka)
2. Dorina'ya mı entegre olacak, bağımsız mı?
3. Veri kaynağın var mı? (Dorina geçmişi, kendi yazıların, web scraping)
4. Türkçe mi İngilizce mi ağırlıklı?
5. Zaman bütçesi? (bir gece mi, hafta sonu mu)
