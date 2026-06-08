# 📈 Session Progress Tracker

## ✅ Completed

### Session 2026-06-05
- [x] Pivot project scope: LLM weak supervision → NER + ABSA murni (keputusan dosen).
- [x] Perbarui `PROJECT_CONTEXT.md`, `SESSION_INITIALIZATION.md`.
- [x] **Sprint 1 SELESAI:** `notebooks/01_data_exploration.ipynb`
  - 10.753 headlines → 14.409 pasangan (headline, entity). Coverage 100%.
  - Output: `data/processed/sentfin_long.csv`
- [x] **Sprint 2 SELESAI (difix & re-run):** `notebooks/02_preprocessing.ipynb`
  - Dedup: 55 identik + 12 konflik ditangani.
  - BIO tagger possessive-aware, stratified split level-headline 80/10/10.
  - Mismatch: 122 → 39 (genuine limitation, excluded dari NER).
  - Output: `ner_{train,val,test}.jsonl`, `absa_{train,val,test}.csv`

### Session 2026-06-06
- [x] Verifikasi Sprint 2 re-run: angka final dikonfirmasi (10.674 headlines, 39 mismatch, split konsisten).
- [x] Install `sklearn-crfsuite` + `seqeval` di Python 3.14 (kernel notebook). Wheel pre-built tersedia.
- [x] **Sprint 3 DITULIS & SMOKE-TESTED:** `notebooks/03_baseline_models.ipynb`
  - **Part A - NER CRF:** feature engineering (window ±2), train CRF, evaluasi seqeval entity-level F1, interpretabilitas transition/state features.
  - **Part B - ABSA TF-IDF+SVM:** input `title [SEP] entity`, LinearSVC `class_weight='balanced'`, evaluasi per-class + breakdown `single/multi-uniform/multi-conflict` untuk mengukur keterbatasan BoW.
  - Smoke test full pipeline lulus di Python 3.14.
- [x] `backend/requirements.txt` diisi lengkap.

---

## ⚠️ Current Blocker / Focus

**Sprint 3 notebook belum di-run dengan data penuh.** Notebook sudah ditulis dan smoke-tested, tapi angka aktual (NER F1, ABSA macro-F1, gap single vs multi-conflict) belum ada.

Yang perlu dikerjakan pertama kali di sesi berikutnya:
1. Buka `notebooks/03_baseline_models.ipynb` → pastikan kernel Python 3.14 → **Kernel → Restart & Run All**
2. Report 3 angka kunci (lihat Next Steps di bawah)

---

## 📝 Next Steps

### Segera (awal sesi berikutnya)
- [ ] Run `03_baseline_models.ipynb` full, report:
  1. **NER CRF entity-level F1** (Part A, sel evaluasi seqeval)
  2. **ABSA macro-F1 + per-class F1** (Part B, classification_report)
  3. **Gap akurasi: single vs multi-conflict** (Part B, sel terakhir) — ini justifikasi empiris Sprint 4

### Sprint 4: Transformer Models (setelah baseline angka masuk)
- [ ] **NER:** Fine-tune RoBERTa/BERT dengan BIO tags (opsi B — subword tokenization + word-to-subword alignment)
- [ ] **ABSA:** Fine-tune transformer dengan format `[CLS] title [SEP] entity [SEP]`, weighted CrossEntropy
- [ ] Bandingkan F1 baseline vs transformer secara tabel

### Sprint 5: Pipeline & Deliverables
- [ ] End-to-end inferensi: `input: headline → {entity: sentiment}`
- [ ] FastAPI serving (opsional tergantung sisa waktu)
- [ ] Kompilasi laporan metodologi

---

## 🧠 Temporary Decisions

- **Format ABSA input:** `[CLS] {headline} [SEP] {entity} [SEP]` — kontekstual, bukan expression-based.
- **Tidak ada LLM labeling** — semua label dari SEntFiN human annotations.
- **Urutan:** Baseline (CRF/SVM) dulu, baru transformer.
- **Split di level headline (`s_no`)** — cegah kebocoran title ke train & test.
- **NER tokenisasi:** word-level (opsi A) untuk baseline; subword (opsi B) untuk transformer Sprint 4.
- **Imbalance:** `class_weight='balanced'` — bukan SMOTE.
- **Normalisasi teks ditunda** — casing utuh untuk NER.
- **Mismatch NER (39 headlines):** excluded dari NER training, tetap di ABSA.
- **Python kernel: 3.14** — satu-satunya yang punya semua library (`sklearn`, `crfsuite`, `seqeval`, `pandas`, `matplotlib`).

---

## 🔑 Temuan Sprint 1 & 2 (baseline referensi)

- 10.753 headlines → 10.674 setelah dedup → 10.635 clean NER.
- Distribusi sentimen entity-level: neutral 38.3%, positive 35.2%, negative 26.5%.
- Entity-span coverage: 100%. Headline length: mean 10 kata / max 23.
- Split final: train 8.539 / val 1.067 / test 1.068 headlines.
- ABSA pairs: train 11.433 / val 1.430 / test 1.448.

---

## 📂 Relevant Files

- `ARTIFACTS/SESSION_INITIALIZATION.md`
- `ARTIFACTS/PROJECT_CONTEXT.md`
- `notebooks/01_data_exploration.ipynb` ✅
- `notebooks/02_preprocessing.ipynb` ✅
- `notebooks/03_baseline_models.ipynb` ⏳ belum di-run penuh
- `data/raw/SEntFiN-v1.1.csv`
- `data/processed/sentfin_long.csv`
- `data/processed/ner_{train,val,test}.jsonl`
- `data/processed/absa_{train,val,test}.csv`
- `backend/models/` (akan terisi setelah Sprint 3 run penuh)
- `backend/requirements.txt`
