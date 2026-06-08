# 📂 Project Context: Financial News Miner

## 1. Executive Summary
Proyek ini adalah pipeline NLP yang berfokus pada dua tugas inti secara berurutan pada *financial news headlines*:
1. **NER (Named Entity Recognition):** Mendeteksi entitas finansial (perusahaan, saham, indeks, dll.) dalam sebuah *headline*.
2. **ABSA (Aspect-Based Sentiment Analysis):** Untuk setiap entitas yang terdeteksi, menentukan sentimen **spesifik terhadap entitas tersebut** berdasarkan konteks keseluruhan *headline*.

> **Catatan Kritis (dari konsultasi dosen):** Pelabelan via LLM dilarang karena bersifat circular — tidak ada nilai tambah jika model akhir hanya belajar dari output LLM. Semua label berasal dari dataset human-annotated.

---

## 2. Dataset: SEntFiN-v1.1.csv

**Sumber:** Sinha, A., Kedas, S., Kumar, R., & Malo, P. (2022). *SEntFiN 1.0: Entity‐aware sentiment analysis for financial news.* JASIST. DOI: https://doi.org/10.1002/asi.24634

**Skema Kolom:**
| Kolom | Deskripsi |
|---|---|
| `S No.` | Index baris |
| `Title` | News headline (input utama model) |
| `Decisions` | Anotasi human: pasangan entity → sentiment (JSON string `{entity: sentiment}`) — **ground truth lengkap untuk NER (keys) + ABSA (values)** |
| `Words` | Jumlah kata di `Title` (word-count), **bukan** daftar entitas — kemungkinan tidak dipakai |

**Statistik Dataset:**
- 10,700+ *headlines* total
- 2,800+ *headlines* dengan **multiple entities** (sering dengan sentimen bertentangan)
- Distribusi kelas entitas: ~4,100 positif, ~3,200 negatif, ~4,500 netral → **cukup seimbang**

**Contoh Anotasi:**
- `"Why Chinese stocks leave US investors vulnerable"` → `{"US": "negative", "Chinese stocks": "neutral"}`
- `"BSE inks strategic partnership with YES Bank"` → `{"YES Bank": "neutral", "BSE": "neutral"}` — *partnership tanpa sinyal finansial eksplisit = neutral*

---

## 3. Core Objectives
1. Membangun model NER yang mampu mengidentifikasi entitas finansial dalam *headline* pendek.
2. Membangun model ABSA yang mampu memberikan label sentimen **per-entitas** berdasarkan konteks penuh *headline* — bukan hanya berdasarkan kata sentimen permukaan.
3. Menyatukan keduanya dalam satu pipeline inferensi end-to-end.
4. Mendokumentasikan performa dengan metrik statistik yang kuat (precision, recall, F1 per kelas).

---

## 4. Architectural Philosophy

### Pipeline Approach (NER → ABSA)
Dua model terpisah yang bekerja secara sekuensial:
- **Model NER** → input: raw headline → output: list of (entity_span, entity_label)
- **Model ABSA** → input: (headline, entity) pair → output: sentiment ∈ {positive, negative, neutral}

### Kunci Desain ABSA: Feature-Based, Bukan Expression-Based
Untuk memastikan model belajar sentimen *contextual* (seperti contoh BSE-YES Bank), input ABSA harus dikonstruksi sebagai:
```
[CLS] {headline} [SEP] {entity} [SEP]
```
Dengan format ini, model melihat **seluruh konteks headline + aspek entitas secara bersamaan**, sehingga bisa membedakan "partnership" (neutral) vs "partnership amid losses" (negative). Model belajar dari sinyal kontekstual, bukan hanya dari kata kunci sentimen.

### Referensi Paper
Paper SEntFiN mengindikasikan RoBERTa sebagai top performer, dengan BERT-based models sebagai *close competitor*. Stack transformer kita akan mengacu pada pendekatan ini.

---

## 5. Tech Stack & Tools (Flexible)

- **Data Processing:** Python 3.10+, Pandas, NumPy, Regex
- **NLP (Classic):** NLTK, spaCy (untuk baseline NER dengan CRF/rule-based)
- **Machine Learning (Baseline):** Scikit-Learn (TF-IDF + SVM/Logistic Regression untuk baseline ABSA)
- **Deep Learning / Transformers:** Hugging Face `transformers`, PyTorch
  - NER: `dslim/bert-base-NER` atau fine-tune RoBERTa
  - ABSA: Fine-tune RoBERTa/FinBERT dengan format `[CLS] headline [SEP] entity [SEP]`
- **Evaluation:** Seqeval (untuk NER), Scikit-learn classification_report (untuk ABSA)
- **Backend API:** FastAPI, Uvicorn (untuk serving pipeline final)
- **Frontend / UI:** Opsional, menyesuaikan sisa waktu sprint

---

## 6. Non-Goals (Explicitly Out of Scope)
- LLM-based labeling atau anotasi otomatis via API (dilarang oleh dosen)
- Document-level sentiment (bukan per-entitas)
- Real-time news scraping (data sudah tersedia via SEntFiN)
