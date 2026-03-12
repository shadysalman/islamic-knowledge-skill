# Islamic Knowledge Skill for Claude

> **The world's first open-source, RAG-powered Islamic knowledge skill for Claude — grounded in 20,972 authenticated records from the Holy Quran, Sahih al-Bukhari, and Sahih Muslim.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Corpus](https://img.shields.io/badge/Corpus-20%2C972%20records-blue)](docs/corpus-reference.md)
[![Sources](https://img.shields.io/badge/Sources-Quran%20%2B%20Bukhari%20%2B%20Muslim-gold)](docs/corpus-reference.md)
[![Anti-Hallucination](https://img.shields.io/badge/Hallucination-RAG%20Protected-red)](docs/anti-hallucination.md)

---

## Why This Exists

Every day, millions of Muslims search for Islamic knowledge online. They get:
- Blog posts with uncited claims
- Social media posts attributing fabricated hadiths to the Prophet ﷺ
- AI responses that sound authoritative but hallucinate Islamic text

This skill fixes that. It gives Claude access to **exact, unmodified, fully cited text** from three of the most authenticated sources in Islamic scholarship — and strictly prevents it from generating or reconstructing any Islamic text from memory.

**No AI-invented hadiths. No paraphrased ayat. Only the authenticated source, verbatim, with full citation.**

---

## The Corpus

| Source | Records | Books/Surahs | Language |
|---|---|---|---|
| Holy Quran | 6,236 ayat | 114 Surahs | Arabic + English (Saheeh International) |
| Sahih al-Bukhari | 7,277 hadiths | 97 Books | Arabic + English + Narrator chain |
| Sahih Muslim | 7,459 hadiths | 57 Books | Arabic + English + Full isnad |
| **Total** | **20,972** | | **Bilingual** |

---

## What It Does

- **Exact verse/hadith lookup**: Ask for Surah 2:255 or Bukhari Book 1 Hadith 1 — get the exact text
- **Topical semantic search**: "What does Islam say about gratitude?" — searches all three sources simultaneously
- **Hadith verification**: "Is this hadith authentic?" — confirms presence or absence in the two Sahihs
- **Cross-referencing**: One query returns Quran + Bukhari + Muslim results together
- **Language-adaptive**: Responds in the language the user writes in (Arabic, English, or bilingual)
- **Scholar-deferring**: Presents text for jurisprudential questions, always defers rulings to qualified scholars

## What It Does NOT Do

- Does not issue fatwas or Islamic legal rulings
- Does not take positions between schools of jurisprudence (Madhabs)
- Does not reference Shia collections or jurisprudence (Sunni scope only)
- Does not generate or reconstruct Islamic text from AI memory
- Does not provide medical advice (presents Prophetic medicine texts as historical/spiritual)

---

## Architecture — How Hallucination is Prevented

```
User Query
    ↓
SKILL.md instructs Claude → Query Supabase Edge Function
    ↓
pgvector semantic search across 20,972 records
    ↓
Database returns EXACT verbatim text + citation
    ↓
Claude presents it — never generates it
```

Claude is a **presenter**, not a generator, of Islamic text. Read the full technical explanation in [docs/anti-hallucination.md](docs/anti-hallucination.md).

---

## Repository Structure

```
islamic-knowledge-skill/
├── SKILL.md                                    ← Install this in Claude
├── README.md
├── LICENSE
├── setup/
│   ├── schema.sql                              ← Supabase tables + pgvector
│   ├── upload_data.py                          ← Data pipeline (all 20,972 records)
│   └── requirements.txt
├── supabase/
│   └── functions/
│       └── islamic-search/
│           └── index.ts                        ← Edge function (the search API)
├── data/
│   └── README.md                               ← Download links for data files
├── examples/
│   └── sample-interactions.md                 ← 15 real Q&A examples
└── docs/
    ├── corpus-reference.md                     ← Full book index (Bukhari + Muslim)
    └── anti-hallucination.md                  ← Technical architecture explanation
```

---

## Setup Guide

### Prerequisites
- Supabase account (free tier works for testing)
- OpenAI API key (for generating search embeddings)
- Claude.ai Pro or Team plan (to install custom skills)

### Step 1 — Set up Supabase

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Go to **Database → Extensions** and enable `vector`
3. Go to **SQL Editor** and run `setup/schema.sql`

### Step 2 — Download the Data

```bash
cd data
curl -L "https://cdn.jsdelivr.net/npm/quran-json@3.1.2/dist/quran_en.json" -o quran_en.json
curl -L "https://raw.githubusercontent.com/AhmedBaset/hadith-json/main/db/by_book/the_9_books/bukhari.json" -o bukhari.json
curl -L "https://raw.githubusercontent.com/AhmedBaset/hadith-json/main/db/by_book/the_9_books/muslim.json" -o muslim.json
```

### Step 3 — Upload to Supabase

```bash
cd setup
pip install -r requirements.txt
python upload_data.py \
  --supabase-url YOUR_SUPABASE_URL \
  --supabase-key YOUR_SERVICE_ROLE_KEY \
  --openai-key YOUR_OPENAI_KEY
```

Expected output:
```
✓ Quran verses:     6,236   ✓
✓ Bukhari hadiths:  7,277   ✓
✓ Muslim hadiths:   7,459   ✓
✓ Total corpus:     20,972  ✓
All records verified. Dataset integrity confirmed.
```

### Step 4 — Deploy the Edge Function

```bash
supabase functions deploy islamic-search
supabase secrets set OPENAI_API_KEY=your_key
```

### Step 5 — Install the Skill in Claude

1. Go to [claude.ai](https://claude.ai) → Settings → Skills
2. Upload the `SKILL.md` file from this repository
3. The skill activates automatically on Islamic knowledge queries

---

## Example Interactions

See [examples/sample-interactions.md](examples/sample-interactions.md) for 15 real Q&A examples including:

- Ayatul Kursi exact lookup
- Hadiths on intentions (Hadith of Niyyah)
- Cross-referencing patience in Quran + Bukhari + Muslim
- Hadith verification (confirming or flagging unverified claims)
- New Muslim Wudu guidance
- Islamic finance (Riba)
- Arabic language responses
- Misinformation checking

---

## Use Cases

This skill serves 1.9 billion Muslims globally and beyond:

| User | How They Use It |
|---|---|
| Practising Muslims | Daily ibadah, Ramadan guidance, quick hadith verification |
| New Muslims | Patient 24/7 foundational learning, no judgment |
| Students | Cross-referencing for essays, Arabic-English lookup |
| Imams & Da'wah workers | Khutbah research, verified source retrieval |
| Muslim families | Parenting guidance, family ethics, inheritance rules |
| Islamic finance professionals | Shariah text references for compliance questions |
| Researchers & academics | Structured search across 20,972 records |
| Counter-extremism workers | Verify or refute claims attributed to the Prophet ﷺ |
| Non-Muslims | Understand what Islamic sources actually say |

---

## Design Principles

**Source transparency** — Every response cites Book + Hadith number or Surah:Ayah. Always verifiable.

**Scholarly humility** — The skill presents text. Qualified scholars issue rulings. This boundary is non-negotiable.

**Madhab neutrality** — No school of jurisprudence is favoured. The text is presented; interpretation is deferred.

**Arabic integrity** — The Arabic text is presented in full, with tashkeel (diacritics), exactly as in the database.

**Sunni scope** — Quran + Bukhari + Muslim. No Shia collections. Clear and honest about its scope.

---

## Roadmap

- **v1.0** (current): Quran + Sahih Bukhari + Sahih Muslim
- **v2.0**: Add the remaining 4 of Kutub al-Sittah (Abu Dawud, Tirmidhi, Nasa'i, Ibn Majah)
- **v3.0**: Riyad al-Salihin + Al-Adab al-Mufrad (character and ethics focus)
- **v4.0**: Basic tafsir layer (Ibn Kathir summaries for key ayat)

---

## Contributing

Contributions are welcome, especially:
- Bug reports on text accuracy (compare against sunnah.com)
- Improvements to the Edge Function search quality
- Additional language support in the SKILL.md
- Documentation improvements

Please open an issue before submitting a PR for significant changes.

---

## License

MIT License — free to use, modify, and distribute with attribution.

See [LICENSE](LICENSE) for full terms.

---

## Author

Built by **Shady** — Quality, Business Improvement & AI Transformation Leader, Dubai.

*"Seek knowledge, for verily seeking knowledge is drawing near to Allah."*
*— Prophetic Tradition*

---

## Disclaimer

This skill is a knowledge access tool. It is not a fatwa-issuing authority, a substitute for qualified Islamic scholarship, or a source of Islamic legal rulings. For personal religious guidance, always consult a qualified scholar.

The Arabic texts and English translations are sourced from open-source datasets and are presented verbatim. Translation accuracy is the responsibility of the original translators (Saheeh International for Quran; AhmedBaset/hadith-json for hadiths).
