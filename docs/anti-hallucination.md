# Anti-Hallucination Architecture

This document explains exactly how the Islamic Knowledge Skill prevents AI-generated or fabricated text from appearing in responses.

---

## The Problem This Solves

Large language models — including Claude — can hallucinate Islamic text. This means they can produce:

- Hadiths that sound authentic but do not exist
- Correct hadith text with wrong book/number citations
- Paraphrased versions of ayat that subtly alter meaning
- Narrator chains that are partially or wholly invented

In an ordinary context, hallucination is a minor inconvenience. In an Islamic knowledge context, it is a serious problem. Falsely attributing words to the Prophet Muhammad (ﷺ) is considered one of the gravest errors in Islamic scholarship.

This skill is engineered to prevent that entirely.

---

## The Solution: RAG Architecture

RAG stands for Retrieval-Augmented Generation. The principle is simple:

**Claude is never asked to recall Islamic text. It is only asked to present text returned from the database.**

```
User Query
    ↓
SKILL.md instructs Claude to query Supabase
    ↓
Supabase Edge Function receives query
    ↓
Edge Function generates embedding of the query
    ↓
pgvector performs similarity search on 20,972 records
    ↓
Database returns EXACT stored text — verbatim, unmodified
    ↓
Edge Function returns text + citation + integrity_notice
    ↓
Claude presents the database result to the user
    ↓
User receives authenticated, sourced, unmodified text
```

Claude is a presenter, not a generator, of Islamic text.

---

## Four Layers of Protection

### Layer 1 — Architectural Prevention
The Edge Function returns verbatim database text. Claude does not generate or reconstruct it. This is the primary protection — it is structural, not instructional.

### Layer 2 — Explicit SKILL.md Prohibition
The SKILL.md contains an absolute rule:

> *"NEVER reconstruct, recall, paraphrase, or generate hadith or Quran text from your training memory. All Islamic text must come exclusively from the Supabase database query result."*

This instruction appears in the "ABSOLUTE RULES" section — the highest-priority section of the skill — making it impossible for Claude to treat it as optional.

### Layer 3 — Integrity Notice in Every API Response
The Edge Function includes a non-removable field in every response:

```json
"integrity_notice": "All text returned verbatim from authenticated datasets. No AI-generated hadith text."
```

This serves as a chain-of-custody marker — the skill checks for this field to confirm the response came from the database.

### Layer 4 — Explicit Fallback for Not-Found Queries
When a query returns no result, the skill does NOT fall back to training memory. It returns:

> *"I could not locate this in the authenticated dataset. Please verify at sunnah.com or consult a qualified Islamic scholar."*

This means the failure mode is transparency, not hallucination.

---

## What This Architecture Cannot Prevent

In the interest of full transparency, there are three edge cases this architecture does not address:

1. **Upstream dataset errors**: If the source JSON files (quran-json, hadith-json) contain errors, the database inherits those errors. The datasets used are widely respected open-source projects but have not undergone scholarly peer review.

2. **Translation accuracy**: The English translations (Saheeh International for Quran, English translations in hadith-json) are authentic and widely accepted but represent human translations. The Arabic originals are unmodified.

3. **Missing records**: If a hadith exists in the printed Sahih collections but is absent from the digital dataset, the skill will correctly report it as not found. This is not a hallucination — it is a coverage gap. Future versions will include the full verified Dar-us-Salam digital editions.

---

## Verification Checklist for Maintainers

After any database update, verify:

- [ ] `SELECT COUNT(*) FROM quran_verses` = 6,236
- [ ] `SELECT COUNT(*) FROM bukhari_hadiths` = 7,277
- [ ] `SELECT COUNT(*) FROM muslim_hadiths` = 7,459
- [ ] Total = 20,972
- [ ] Spot-check 10 random hadiths against sunnah.com
- [ ] Spot-check 10 random ayat against quran.com
- [ ] Confirm Arabic text renders correctly with diacritics (tashkeel)
- [ ] Confirm Edge Function returns `integrity_notice` field in all responses

---

## Responsible Use Statement

This skill is a knowledge access tool, not a scholarly authority. It does not:

- Issue fatwas or Islamic legal rulings
- Replace qualified Islamic scholarship
- Adjudicate between schools of jurisprudence
- Make determinations about hadith authenticity beyond confirming presence in the two Sahihs

Every response that involves personal practice, legal questions, or contested interpretations includes a recommendation to consult a qualified Islamic scholar.
