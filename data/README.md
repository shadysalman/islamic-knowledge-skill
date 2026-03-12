# Data Sources

The dataset files are not included in this repository due to file size (combined ~37MB).
Download them from the original open-source sources below and place them in this `/data` folder.

---

## Required Files

| Filename | Source | Size |
|---|---|---|
| `quran_en.json` | quran-json on npm | ~2.4 MB |
| `bukhari.json` | AhmedBaset/hadith-json | ~12.7 MB |
| `muslim.json` | AhmedBaset/hadith-json | ~11.5 MB |

---

## Download Commands

```bash
# Option 1: Download via CDN (fastest)
curl -L "https://cdn.jsdelivr.net/npm/quran-json@3.1.2/dist/quran_en.json" -o quran_en.json

curl -L "https://raw.githubusercontent.com/AhmedBaset/hadith-json/main/db/by_book/the_9_books/bukhari.json" -o bukhari.json

curl -L "https://raw.githubusercontent.com/AhmedBaset/hadith-json/main/db/by_book/the_9_books/muslim.json" -o muslim.json
```

```bash
# Option 2: Install via npm
npm install quran-json
cp node_modules/quran-json/dist/quran_en.json ./quran_en.json
```

---

## Verify Your Downloads

After downloading, run this check to confirm record counts:

```python
import json

with open('quran_en.json') as f:
    quran = json.load(f)
total_ayat = sum(s['total_verses'] for s in quran)
print(f"Quran: {len(quran)} surahs, {total_ayat} ayat")  # Expected: 114 surahs, 6236 ayat

with open('bukhari.json') as f:
    bukhari = json.load(f)
print(f"Bukhari: {len(bukhari['hadiths'])} hadiths")  # Expected: 7277

with open('muslim.json') as f:
    muslim = json.load(f)
print(f"Muslim: {len(muslim['hadiths'])} hadiths")  # Expected: 7459
```

---

## Source Attribution

- **Quran**: Arabic text from The Noble Qur'an Encyclopedia (Uthmani script). English translation by Umm Muhammad (Saheeh International) sourced from tanzil.net.
- **Sahih al-Bukhari & Sahih Muslim**: From [AhmedBaset/hadith-json](https://github.com/AhmedBaset/hadith-json) — a comprehensive JSON-formatted hadith database containing both Arabic and English text.

All sources are open-source and freely available for non-commercial and educational use.
