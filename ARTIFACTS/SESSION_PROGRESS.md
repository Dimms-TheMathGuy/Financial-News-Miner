# 📈 Session Progress Tracker

## ✅ Completed (Session 2026-06-05)

- [x] **PIVOT:** Rombak total project scope — dari LLM weak supervision ke NER + ABSA murni (keputusan dosen).
- [x] Perbarui `PROJECT_CONTEXT.md`, `SESSION_INITIALIZATION.md` sesuai scope baru.
- [x] **Sprint 1 SELESAI & divalidasi:** `notebooks/01_data_exploration.ipynb`
  - Parse `SEntFiN-v1.1.csv` → 0 failures, 0 label kotor.
  - Explode ke long-format `(s_no, title, entity, sentiment)`.
  - EDA distribusi, verifikasi klaim README.
  - **Entity-span coverage: 100%** → BIO auto-labeling via substring-matching layak.
  - Output: `data/processed/sentfin_long.csv`
- [x] **Sprint 2 DITULIS & DIFIX:** `notebooks/02_preprocessing.ipynb`
  - Investigasi 67 duplikat → 55 identik, 12 konflik.
  - Dedup: buang semua konflik, keep s_no terkecil untuk identik.
  - Stratified split level-headline 80/10/10 → distribusi sentimen antar-split konsisten (±1%).
  - BIO tagger dengan possessive-aware boundary check (`HULs`, `FTILs`, dll).
  - Fix validasi mismatch (per-entity, bukan total B-ENT count).
  - Mismatch headlines dikecualikan dari NER, tetap masuk ABSA.

---

## ⚠️ Current Blocker / Focus

**Sprint 2 notebook perlu di-run ulang dari awal (Kernel → Restart & Run All) sebelum Sprint 3 dimulai.**

Alasan: patch dilakukan setelah run pertama. Sel dedup (sel-5) mengubah `long_df` yang dipakai semua sel sesudahnya — run parsial tidak aman.

Hal yang perlu dikonfirmasi dari run ulang:
- Berapa mismatch tersisa setelah fix possessive? (Ekspektasi: turun dari 122 ke ~20-40)
- Angka final NER clean headlines per split
- Output files `ner_{train,val,test}.jsonl` dan `absa_{train,val,test}.csv` ter-overwrite dengan versi bersih

**Minor non-blocker (catat untuk nanti):** Di sel-11 `02_preprocessing.ipynb`, filter `t.count('B-ENT') >= 2` bisa crash `.iloc[0]` jika semua multi-entity clean headlines sudah habis. Tidak perlu difix sekarang.

---

## 📝 Next Steps (Sprint 3 — setelah run ulang Sprint 2 dikonfirmasi)

### Sprint 3a: NER Baseline (CRF / spaCy rule-based)
- [ ] **N-01:** Load `ner_train.jsonl`, definisikan fitur token sederhana (token string, prefix/suffix, is_upper, is_digit, prev/next token)
- [ ] **N-02:** Latih CRF dengan `sklearn-crfsuite` atau spaCy NER blank model
- [ ] **N-03:** Evaluasi dengan `seqeval` — precision, recall, F1 per-entity-type
- [ ] **N-04:** Error analysis: tipe mismatch apa yang paling banyak? (partial match, false positive, false negative)

### Sprint 3b: ABSA Baseline (TF-IDF + SVM)
- [ ] **A-01:** Load `absa_train.csv`, buat fitur: gabung `title + " [SEP] " + entity` sebagai input string
- [ ] **A-02:** TF-IDF vectorizer → SVM dengan `class_weight='balanced'`
- [ ] **A-03:** Evaluasi: per-class precision/recall/F1, confusion matrix
- [ ] **A-04:** Error analysis: kasus neutral yang salah diklasifikasi paling sering terjadi di konteks apa?

---

## 🧠 Temporary Decisions

- **Format ABSA input:** `[CLS] {headline} [SEP] {entity} [SEP]` — keputusan arsitektural kunci agar model belajar sentimen kontekstual.
- **Tidak ada LLM labeling** — semua label dari SEntFiN human annotations.
- **Urutan prioritas model:** Baseline dulu (CRF/SVM), baru fine-tune transformer.
- **Split di level headline (`s_no`)** — cegah kebocoran title ke train & test.
- **NER tokenisasi: word-level (opsi A)** saat ini; opsi B (subword alignment) saat fine-tuning transformer.
- **Imbalance: `class_weight='balanced'`** — bukan SMOTE (SMOTE tidak cocok untuk text classifier).
- **Normalisasi teks ditunda** — casing & simbol dibiarkan utuh karena relevan untuk NER.
- **Mismatch headlines:** dikecualikan dari NER training saja; tetap masuk ABSA data (label sentimen tetap valid).

---

## 🔑 Temuan Sprint 1 (terverifikasi dari data)

- Total: **10.753 headlines** → **14.409 pasangan (headline, entity)** setelah explode.
- Multi-entity headlines: **2.850** (cocok klaim README).
- Conflicting-sentiment headlines: **1.235** (43% dari multi-entity) → justifikasi kuat ABSA.
- Distribusi sentimen: neutral **38.3%**, positive **35.2%**, negative **26.5%** — moderate imbalance.
- **Entity-span coverage: 100%** → BIO tagging via substring-matching layak.
- Panjang headline: mean 10 kata / max 23 → `max_length=64` cukup untuk BERT.
- Kolom `Words` = word-count, bukan daftar entitas → diabaikan.

---

## 📂 Relevant Files

- `ARTIFACTS/SESSION_INITIALIZATION.md`
- `ARTIFACTS/PROJECT_CONTEXT.md`
- `notebooks/01_data_exploration.ipynb` ✅ done
- `notebooks/02_preprocessing.ipynb` ⚠️ perlu re-run
- `data/raw/SEntFiN-v1.1.csv`
- `data/processed/sentfin_long.csv`
- `data/processed/ner_{train,val,test}.jsonl` (akan di-overwrite saat re-run)
- `data/processed/absa_{train,val,test}.csv` (akan di-overwrite saat re-run)
