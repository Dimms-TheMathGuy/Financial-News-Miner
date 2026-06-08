# 📚 Knowledge Capture: Software Engineering Concepts

*This file contains reusable concepts, idioms, and patterns discovered during development. The agent will append new entries here at session termination.*

---

## Template for New Entries (Do not overwrite, append below)

### Concept: [Name of Concept]
- **What it is:** - **Why it matters:** - **When to use it:** - **How it appears in this project:** - **Small example or syntax sketch:** - **Common mistakes:** ---

---

## Entries

---

### Concept: Split di Level Entity vs Level Headline (Mencegah Data Leakage)

- **What it is:** Ketika dataset memiliki hierarki (headline → banyak pasangan entity), unit split harus ditentukan di level teratas (headline), bukan level bawah (entity/row).
- **Why it matters:** Jika split dilakukan per-row, satu headline yang sama bisa muncul di training dan test sekaligus. Model akan "melihat" kalimat test saat training — ini adalah kebocoran data (data leakage) yang menggelembungkan metrik evaluasi secara artifisial.
- **When to use it:** Setiap kali dataset memiliki relasi one-to-many: dokumen → kalimat, artikel → paragraf, headline → entitas, dll.
- **How it appears in this project:** `train_test_split` dilakukan pada array `s_no` (headline id), lalu semua entitas dari s_no yang sama otomatis masuk ke split yang sama.
  ```python
  train_sno, temp_sno = train_test_split(snos, stratify=y, ...)  # bukan long_df rows
  long_df['split'] = long_df['s_no'].map(split_of)
  ```
- **Common mistakes:**
  - Langsung `train_test_split(long_df, ...)` — memisahkan baris tanpa memperhitungkan bahwa rows dari headline yang sama harus masuk ke satu split.
  - Stratifikasi pada label entitas langsung tanpa aggregasi — bucket langka untuk kombinasi multi-entitas bisa crash.

---

### Concept: Stratifikasi pada Majority Label untuk Multi-Label Samples

- **What it is:** Teknik membuat stratified split ketika setiap sample memiliki beberapa label (multi-entity, multi-label). Aggregasi ke satu label representatif (majority vote) sebelum `stratify=`.
- **Why it matters:** `train_test_split(stratify=)` butuh satu label per sample. Kombinasi label multi-entitas menghasilkan terlalu banyak bucket langka → error.
- **When to use it:** Dataset dengan multi-entity per sample (seperti SEntFiN), multi-label classification.
- **How it appears in this project:**
  ```python
  maj = long_df.groupby('s_no')['sentiment'].agg(lambda s: s.value_counts().idxmax())
  train_sno, _ = train_test_split(snos, stratify=maj.values, ...)
  ```
- **Common mistakes:**
  - Menggunakan kombinasi label sebagai strata langsung → bucket langka crash.
  - Tidak memverifikasi distribusi entity-level setelah split — stratifikasi majority bisa tidak mewakili distribusi aktual entity.

---

### Concept: Notebook sebagai Research Layer, bukan Production Layer

- **What it is:** Pemisahan tanggung jawab: notebook untuk eksperimen, eksplorasi, dan validasi; backend/module untuk kode yang di-deploy atau dipanggil berulang.
- **Why it matters:** Notebook yang berisi logika produksi menjadi sulit di-debug, di-test, dan di-maintain. Notebook sebaiknya hanya berisi alur eksplorasi yang linear.
- **When to use it:** Selalu terapkan dalam proyek ML yang akan punya komponen serving (API, pipeline).
- **How it appears in this project:** Format input ABSA (`[CLS] title [SEP] entity [SEP]`) tidak di-build di preprocessing notebook — komponen mentah `(title, entity)` disimpan, perakitan dilakukan di training script. Ini menjaga data model-agnostic.
- **Common mistakes:**
  - Menyertakan format tokenizer spesifik (BERT vs RoBERTa) di data preprocessing — akan harus diubah setiap ganti model.
  - Hardcode path atau konfigurasi di dalam notebook — gunakan variabel `PROJECT_ROOT` dan pathlib.
