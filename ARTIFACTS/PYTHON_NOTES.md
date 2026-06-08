# 📚 Knowledge Capture: Python Concepts

*This file contains reusable concepts, idioms, and patterns discovered during development. The agent will append new entries here at session termination.*

---

## Template for New Entries (Do not overwrite, append below)

### Concept: [Name of Concept]
- **What it is:** - **Why it matters:** - **When to use it:** - **How it appears in this project:** - **Small example or syntax sketch:** - **Common mistakes:** ---

---

## Entries

---

### Concept: `itertuples` vs `iterrows` untuk Iterasi DataFrame

- **What it is:** Dua cara iterasi baris DataFrame di pandas. `itertuples()` mengembalikan namedtuple per baris; `iterrows()` mengembalikan `(index, Series)`.
- **Why it matters:** `itertuples` ~10× lebih cepat dari `iterrows` karena tidak membungkus baris dalam `Series` object. Untuk 10k+ baris, perbedaannya terasa.
- **When to use it:** Gunakan `itertuples` jika hanya perlu baca nilai kolom. Gunakan `iterrows` jika perlu akses ke index atau butuh fleksibilitas Series (jarang diperlukan).
- **How it appears in this project:** Di `01_data_exploration.ipynb` — loop explode `decisions` JSON ke long format.
  ```python
  for r in df.itertuples(index=False):
      for ent, sent in r.parsed.items():
          records.append({'s_no': r.s_no, ...})
  ```
- **Common mistakes:**
  - Kolom dengan nama tidak valid sebagai Python identifier (misal `S No.`) tidak bisa diakses dengan `r.s_no` — rename kolom dulu.
  - `itertuples` tidak mendukung assignment balik ke DataFrame — jika perlu update, gunakan `df.at[idx, col] = val` atau vektorisasi.

---

### Concept: `frozenset` sebagai Hashable Signature

- **What it is:** `frozenset` adalah versi immutable dari `set` — bisa dijadikan key dict atau elemen set lain.
- **Why it matters:** `set` biasa tidak hashable, tidak bisa dipakai di operasi seperti `nunique()` atau sebagai dict key. `frozenset` bisa.
- **When to use it:** Saat perlu membandingkan himpunan tanpa memperhatikan urutan, dan hasilnya perlu di-hash.
- **How it appears in this project:** Di `02_preprocessing.ipynb` — membuat "signature" per headline untuk deteksi duplikat:
  ```python
  sig = long_df.groupby('s_no').apply(
      lambda g: frozenset(zip(g['entity'], g['sentiment']))
  )
  # Lalu: grp['signature'].nunique() — bisa karena frozenset hashable
  ```
- **Common mistakes:**
  - Mencoba `set(zip(...))` lalu memanggil `nunique()` — gagal karena `set` tidak hashable.
  - Lupa bahwa `frozenset` mengabaikan duplikat — jika satu entitas muncul dua kali dengan sentimen beda dalam satu headline, salah satu akan hilang.
