# 📈 Session Progress Tracker

## ✅ Completed
- [x] **D-01:** Setup GitHub repo, struktur folder, & integrasi `.gitkeep`.
- [x] Pembuatan folder `ARTIFACTS/` dan inisialisasi file pedoman AI.
- [x] **PIVOT:** Rombak total project scope — dari LLM weak supervision ke NER + ABSA murni dengan dataset human-annotated (SEntFiN-v1.1.csv).

## ⏳ Current Status
- Sprint 1 SELESAI & divalidasi. Sprint 2 (preprocessing) notebook ditulis, menunggu user run.

---

## 🔑 Temuan Sprint 1 (terverifikasi dari data)
- Total: **10.753 headlines** → **14.409 pasangan (headline, entity)** setelah explode.
- Multi-entity headlines: **2.850** (cocok klaim README).
- Conflicting-sentiment headlines: **1.235** (43% dari multi-entity) → justifikasi kuat untuk ABSA.
- Distribusi sentimen (entity-level): neutral **5.515 (38%)**, positive **5.075 (35%)**, negative **3.819 (27%)** → moderate imbalance, bukan parah. Pakai `class_weight`/weighted loss, **bukan SMOTE**.
- **Entity-span coverage: 100%** → auto-labeling NER via span-matching LAYAK (skema BIO standar).
- Parse failures: 0, tidak ada label kotor.
- Panjang headline: mean 10 kata / max 23 → `max_length=64` cukup untuk BERT, training cepat.
- ⚠️ **67 duplicate titles** → ditangani di Sprint 2 (cegah leakage).
- Kolom `Words` = word-count, **bukan** entitas → diabaikan.

---

## 📝 Undone Tasks (Sprint Backlog)

### Sprint 1: Data Exploration & Schema Understanding ✅
- [x] **D-02:** Load `SEntFiN-v1.1.csv`, cek null/dtype/duplikat → `notebooks/01_data_exploration.ipynb`
- [x] **D-03:** Parse `Decisions` (JSON) → 0 failures
- [x] **D-04:** EDA distribusi (entitas/headline, sentimen, panjang)
- [x] **D-05:** Edge cases: conflicting sentiment + entity-span coverage (insight baru, di luar plan awal)
- [x] Output: `data/processed/sentfin_long.csv`

### Sprint 2: Data Preprocessing & Format Conversion (notebook ditulis)
- [~] **E-01:** Investigasi & dedup 67 duplikat title (cegah leakage)
- [~] **E-02:** NER BIO tagging **word-level (opsi A)**, single type `ENT`, dgn boundary check
- [~] **E-03:** ABSA format: `(title, entity)` + label int `{neg:0, neu:1, pos:2}`
- [~] **E-04:** Stratified split **level-headline** (stratify majority-sentiment), 80/10/10
- [ ] **E-05:** *(Ditunda)* Normalisasi teks minimal — diputuskan saat modelling agar casing tetap utuh untuk NER

### Sprint 3: NER Model
- [ ] **N-01:** Baseline NER — spaCy rule-based / CRF dengan fitur token sederhana
- [ ] **N-02:** Fine-tune transformer untuk NER (RoBERTa atau BERT dengan BIO tags)
- [ ] **N-03:** Evaluasi NER: precision, recall, F1 per entity-type dengan `seqeval`
- [ ] **N-04:** Error analysis: false positives/negatives — apakah model miss entitas pendek atau multi-token?

### Sprint 4: ABSA Model
- [ ] **A-01:** Baseline ABSA — TF-IDF + SVM dengan input `headline + entity` sebagai fitur gabungan
- [ ] **A-02:** Fine-tune transformer untuk ABSA dengan format input `[CLS] headline [SEP] entity [SEP]`
- [ ] **A-03:** Evaluasi ABSA: per-class precision, recall, F1 — fokus pada kelas netral (paling sulit dibedakan)
- [ ] **A-04:** Error analysis: apakah model bisa membedakan "partnership" (neutral) vs "partnership amid losses" (negative)?

### Sprint 5: Pipeline & Deliverables
- [ ] **P-01:** Gabungkan NER + ABSA menjadi satu fungsi inferensi end-to-end: `input: headline → output: {entity: sentiment}`
- [ ] **P-02:** FastAPI endpoint untuk serving pipeline
- [ ] **P-03:** Kompilasi notebook, tulis kesimpulan metodologi, ekspor model final
- [ ] **P-04 (Opsional):** Frontend UI sederhana

---

## 🧠 Temporary Decisions
- **Format ABSA input:** `[CLS] {headline} [SEP] {entity} [SEP]` — keputusan arsitektural kunci agar model belajar sentimen kontekstual.
- **Tidak ada LLM labeling** — semua label dari SEntFiN human annotations.
- **Urutan prioritas model:** Baseline dulu (CRF/SVM), baru fine-tune transformer. Jangan skip baseline.
- **Split di level headline (`s_no`), bukan per-pasangan** — cegah kebocoran title yang sama ke train & test.
- **NER tokenisasi: mulai word-level (opsi A)**; opsi B (subword alignment) dipertimbangkan saat fine-tuning transformer Sprint 3.
- **Imbalance: pakai `class_weight`/weighted loss, bukan SMOTE** (SMOTE tidak cocok untuk sequence/text classifier).
- **Normalisasi teks ditunda** — casing & simbol dibiarkan utuh karena relevan untuk NER; keputusan cleaning diambil per-model saat modelling.

---

## 📂 Relevant Files
- `ARTIFACTS/SESSION_INITIALIZATION.md`
- `ARTIFACTS/PROJECT_CONTEXT.md`
- `data/raw/SEntFiN-v1.1.csv` *(belum diverifikasi exist — cek di Sprint 1)*
