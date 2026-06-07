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

---

### Concept: CRF (Conditional Random Field) untuk NER — kenapa bukan per-token classifier

- **What it is:** Model discriminatif untuk sequence labeling. Memodelkan P(y₁...yₙ | x₁...xₙ) — probabilitas joint seluruh label sequence given seluruh input. Library: `sklearn-crfsuite`.
- **Why it matters:** Per-token classifier (SVM/LR per token) memprediksi tiap label secara independen — tidak bisa menegakkan constraint sekuens seperti `I-ENT` tidak boleh muncul tanpa `B-ENT` sebelumnya. CRF bisa karena dia memodelkan transisi antar-label.
- **When to use it:** Baseline NER sebelum neural/transformer. Juga cocok untuk dataset dengan entitas yang memiliki ciri tipografi kuat (kapitalisasi, suffix) karena CRF bisa memanfaatkan fitur arbitrary.
- **How it appears in this project:** `ner_crf_baseline.joblib` di `backend/models/`. Dilatih pada `ner_train.jsonl`, dievaluasi dengan `seqeval`.
  ```python
  from sklearn_crfsuite import CRF
  crf = CRF(algorithm='lbfgs', c1=0.1, c2=0.1, max_iterations=100,
            all_possible_transitions=True)
  crf.fit(X_train, y_train)  # X_train = list of list of feature dicts
  ```
- **Common mistakes:**
  - Menggunakan token-accuracy sebagai metric — terlihat ~95% palsu karena mayoritas token = `O`. Gunakan `seqeval` (entity-level span F1).
  - Tidak menggunakan `all_possible_transitions=True` — CRF tidak belajar transisi ilegal yang tidak muncul di train (mis. `O → I-ENT`).
  - Fitur terlalu sederhana (hanya token string) — tambahkan konteks window ±2 dan fitur tipografi untuk financial NER.

---

### Concept: `seqeval` — entity-level F1 untuk NER (vs token-accuracy)

- **What it is:** Library evaluasi untuk sequence labeling (NER). Menghitung Precision, Recall, F1 di level **span entitas** — bukan per-token.
- **Why it matters:** Token-accuracy pada NER dataset yang padat `O` (~80-90% token = O) akan selalu terlihat tinggi meski model tidak mendeteksi entitas sama sekali. `seqeval` mengabaikan token `O` dan hanya menilai apakah span entitas diprediksi dengan benar (mulai dan akhir span harus tepat).
- **When to use it:** Selalu untuk evaluasi NER. Jangan pakai `sklearn.metrics.f1_score` flat untuk NER.
- **How it appears in this project:**
  ```python
  from seqeval.metrics import classification_report, f1_score
  # y_true & y_pred = list of list of BIO tag strings
  print(classification_report(test_labels, y_pred))
  # Output: precision, recall, F1 per entity type + micro/macro
  ```
- **Common mistakes:**
  - Partial match dihitung salah — prediksi `B-ENT` benar tapi `I-ENT` salah = entity **salah total** (bukan partial credit).
  - Menggunakan `average='micro'` di sklearn flat — ini salah untuk sequence labeling.

---

### Concept: TF-IDF + LinearSVC untuk ABSA Baseline & Keterbatasan BoW

- **What it is:** TF-IDF mengkonversi teks ke vektor sparse (bobot berbanding terbalik frekuensi dokumen). LinearSVC menemukan hyperplane optimal di ruang fitur tersebut.
- **Why it matters:** Untuk ABSA, input adalah `title [SEP] entity`. BoW kehilangan informasi posisi — dua entitas dengan sentimen berbeda dalam satu headline akan memiliki vektor title yang identik. Ini batas teoretis BoW untuk ABSA.
- **When to use it:** Sebagai baseline cepat. Jika gap antara akurasi `single-entity` vs `multi-conflict` besar, itu bukti empiris bahwa transformer diperlukan.
- **How it appears in this project:**
  ```python
  from sklearn.feature_extraction.text import TfidfVectorizer
  from sklearn.svm import LinearSVC
  v = TfidfVectorizer(ngram_range=(1,2), min_df=2, sublinear_tf=True)
  svm = LinearSVC(class_weight='balanced', C=1.0)
  svm.fit(v.fit_transform(train['text']), train['label'])
  ```
- **Common mistakes:**
  - `min_df=1` — menyertakan fitur yang hanya muncul sekali (noise, memperlambat training).
  - `sublinear_tf=False` — tanpa ini, entitas yang disebut 10× dapat bobot 10× lebih besar, padahal seharusnya lebih kecil.
  - Tidak memecah evaluasi per `head_type` (single/multi-conflict) — kehilangan insight kunci tentang keterbatasan model.
