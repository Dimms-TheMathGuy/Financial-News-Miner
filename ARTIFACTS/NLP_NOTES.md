# 📚 Knowledge Capture: NLP Concepts

*This file contains reusable concepts, idioms, and patterns discovered during development. The agent will append new entries here at session termination.*

---

## Template for New Entries (Do not overwrite, append below)

### Concept: [Name of Concept]
- **What it is:** - **Why it matters:** - **When to use it:** - **How it appears in this project:** - **Small example or syntax sketch:** - **Common mistakes:** ---

---

## Entries

---

### Concept: BIO Tagging (Named Entity Recognition)

- **What it is:** Format anotasi token untuk NER. Setiap token diberi satu dari tiga label: `B-ENT` (Begin — token pertama dari entitas), `I-ENT` (Inside — token berikutnya dalam entitas yang sama), `O` (Outside — bukan entitas).
- **Why it matters:** Memberikan informasi batas dan panjang entitas kepada model. Tanpa format ini, model tidak tahu apakah "YES Bank" adalah satu entitas atau dua.
- **When to use it:** Selalu digunakan untuk sequence labeling / NER dengan model berbasis token (CRF, BERT-NER, dll).
- **How it appears in this project:** `ner_{train,val,test}.jsonl` — setiap baris berisi `{"tokens": [...], "ner_tags": [...]}`. Entitas di SEntFiN hanya satu tipe sehingga dipakai label `ENT` tunggal (bukan `ORG`, `PER`, dll).
- **Small example:**
  ```
  Judul: "BSE inks strategic partnership with YES Bank"
  Tokens : [BSE, inks, strategic, partnership, with, YES, Bank]
  BIO    : [B-ENT, O, O, O, O, B-ENT, I-ENT]
  ```
- **Common mistakes:**
  - Menghitung `B-ENT count == len(entities)` sebagai invariant — salah jika satu entity muncul >1× di kalimat (B-ENT count bisa lebih besar, tapi itu benar).
  - Tidak melakukan boundary check: `Gold` ikut ter-tag di dalam `Golden`.
  - Tidak menangani possessive tanpa apostrof: `HULs` — `s` setelah match dianggap alnum, padahal ini suffix possessive yang umum di news headlines.

---

### Concept: Character-Level Boundary Check untuk Substring Matching

- **What it is:** Validasi bahwa kemunculan substring entity benar-benar berdiri sendiri sebagai kata/frasa, bukan bagian dari kata lebih panjang. Dilakukan dengan mengecek karakter tepat sebelum dan sesudah match.
- **Why it matters:** Substring matching naif akan menghasilkan false positive (misalnya `Nifty` ter-tag di dalam `Nifty50`).
- **When to use it:** Setiap kali mencari entitas berupa teks dalam kalimat tanpa informasi offset yang diberikan.
- **How it appears in this project:** Fungsi `find_entity_charspans` di `02_preprocessing.ipynb`.
- **Small example:**
  ```python
  # Standard boundary:
  left  = (a == 0) or (not title[a-1].isalnum())
  right = (b == len(title)) or (not title[b].isalnum())
  # Possessive extension (HULs, FTILs, PMC Infratechs):
  if not right and title[b].lower() == 's':
      after_s = b + 1
      right = (after_s >= len(title)) or (not title[after_s].isalnum())
  ```
- **Common mistakes:**
  - Lupa case-insensitive match (`re.IGNORECASE`).
  - Tidak menggunakan `re.escape(entity)` — entity bisa mengandung karakter regex seperti `&`, `.`, `(`.
  - Tidak menangani possessive suffix → banyak news entities akan miss (HUL, FTIL, dll).

---

### Concept: ABSA — Feature-Based vs Expression-Based Sentiment

- **What it is:** Dua pendekatan berbeda dalam ABSA (Aspect-Based Sentiment Analysis).
  - **Expression-based:** mencari kata sentimen eksplisit (positive/negative lexicon) di sekitar entitas.
  - **Feature-based:** menggunakan representasi kontekstual penuh (seluruh kalimat + aspek) untuk inferensi sentimen.
- **Why it matters:** Expression-based akan gagal pada kasus seperti `"BSE inks strategic partnership with YES Bank"` — tidak ada kata sentimen eksplisit, tapi sentimen yang benar adalah neutral. Feature-based menangkap ini karena model belajar dari distribusi konteks secara keseluruhan.
- **When to use it:** Feature-based selalu lebih kuat untuk teks finansial pendek yang padat informasi.
- **How it appears in this project:** Input ABSA dikonstruksi sebagai `[CLS] {headline} [SEP] {entity} [SEP]`. Model melihat headline penuh + entitas target sekaligus, sehingga bisa inferensi kontekstual.
- **Common mistakes:**
  - Memisahkan headline dari entitas dan hanya memberi entitas saja ke model — model kehilangan konteks.
  - Hanya memberi entity tanpa headline — untuk kalimat ambigu seperti "Gold shines" (Gold = positive), tapi "Gold loses luster" (Gold = negative), model butuh kalimat penuh.

---

### Concept: Tokenisasi Word-Level dengan Offset Karakter

- **What it is:** Tokenisasi berbasis whitespace (`\S+`) yang menyimpan posisi karakter (start, end) setiap token di string asli.
- **Why it matters:** Offset diperlukan untuk memetakan span entitas (char-level) ke token (word-level). Tanpa offset, mapping entity → token harus dilakukan dengan heuristik yang rapuh.
- **When to use it:** Untuk NER word-level (opsi A). Untuk transformer NER (opsi B), pakai tokenizer dari Hugging Face yang menghasilkan offset otomatis via `return_offsets_mapping=True`.
- **How it appears in this project:**
  ```python
  def tokenize_with_spans(text):
      return [(m.group(), m.start(), m.end()) for m in re.finditer(r'\S+', text)]
  ```
- **Common mistakes:**
  - Menggunakan `str.split()` — tidak menghasilkan offset, hanya token strings.
  - Lupa bahwa `\S+` akan menyertakan tanda baca yang melekat pada token (`Bank,` bukan `Bank`). Perlu diantisipasi saat boundary check.
