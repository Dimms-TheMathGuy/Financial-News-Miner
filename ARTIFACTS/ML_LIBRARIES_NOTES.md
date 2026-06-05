# 📚 Knowledge Capture: ML Libraries & Patterns

*This file contains reusable concepts, idioms, and patterns discovered during development. The agent will append new entries here at session termination.*

---

## Template for New Entries (Do not overwrite, append below)

### Concept: [Name of Concept]
- **What it is:** - **Why it matters:** - **When to use it:** - **How it appears in this project:** - **Small example or syntax sketch:** - **Common mistakes:** ---

---

## Entries

---

### Concept: Penanganan Class Imbalance — `class_weight` vs SMOTE

- **What it is:** Dua strategi berbeda untuk menangani distribusi kelas yang tidak seimbang:
  - `class_weight='balanced'`: memberi bobot lebih tinggi pada kelas minoritas saat menghitung loss. Model tetap belajar dari data asli, hanya loss-nya yang dibobot.
  - **SMOTE** (Synthetic Minority Over-sampling Technique): membuat sampel sintetis baru dari kelas minoritas dengan interpolasi di feature space.
- **Why it matters:** SMOTE dirancang untuk feature vector tabular/numerik (mis. TF-IDF matrix, numerical embeddings). Tidak bisa diaplikasikan langsung pada raw text atau sequence. Menggunakannya pada text classifier akan menghasilkan feature space yang tidak bermakna.
- **When to use it:**
  - `class_weight='balanced'` → **selalu aman** untuk classifier berbasis probabilitas (SVM, Logistic Regression, fine-tuned transformer).
  - SMOTE → hanya untuk tabular data atau setelah feature extraction (mis. pada TF-IDF matrix, **bukan** pada raw text).
- **How it appears in this project:** Dataset SEntFiN memiliki imbalance moderat: negative 26.5% vs neutral 38.3% vs positive 35.2%. Solusi: `class_weight='balanced'` di sklearn, `class_weights` tensor di PyTorch `CrossEntropyLoss`. SMOTE tidak dipakai.
- **Common mistakes:**
  - Mengaplikasikan SMOTE pada teks mentah — tidak bermakna secara matematis.
  - Tidak menerapkan apapun dan mengabaikan imbalance — akan menghasilkan model yang bias ke kelas mayoritas dan metric accuracy yang menyesatkan.

---

### Concept: Pandas `pd.crosstab(..., normalize='index')` untuk Verifikasi Distribusi Split

- **What it is:** `pd.crosstab` membuat tabel kontingensi; `normalize='index'` mengkonversinya ke proporsi per baris.
- **Why it matters:** Cara cepat untuk memverifikasi apakah stratified split menghasilkan distribusi label yang konsisten antar-split.
- **When to use it:** Setelah setiap train/val/test split, sebagai sanity check wajib.
- **How it appears in this project:**
  ```python
  pd.crosstab(long_df['split'], long_df['sentiment'], normalize='index').round(3)
  # Output: proporsi negative/neutral/positive per split — harus mirip antara train/val/test
  ```
- **Common mistakes:**
  - Hanya cek ukuran split (`len`), tidak distribusi label — bisa ada split yang seimbang ukurannya tapi skewed distribusi labelnya.

---

### Concept: JSONL sebagai Format Penyimpanan untuk Sequence Data (NER)

- **What it is:** JSON Lines — setiap baris adalah satu JSON object yang valid. Berbeda dari JSON array (yang memuat seluruh dataset dalam satu struktur).
- **Why it matters:** Untuk dataset NER, setiap sampel adalah list token + list tag (panjang bervariasi per kalimat). JSONL lebih mudah di-stream baris per baris tanpa load seluruh file ke memori; juga lebih mudah di-debug (buka teks editor, lihat satu baris = satu sampel).
- **When to use it:** Sequence data dengan panjang bervariasi per sampel: NER, sequence labeling, text generation.
- **How it appears in this project:** `ner_{train,val,test}.jsonl` — setiap baris: `{"s_no": 1, "tokens": [...], "ner_tags": [...]}`.
- **Common mistakes:**
  - Menyimpan sebagai CSV — nested list (tokens, tags) harus di-serialize lagi, rawan parsing error.
  - Menyimpan sebagai satu JSON array besar — tidak bisa di-stream, harus load semua ke memori.
