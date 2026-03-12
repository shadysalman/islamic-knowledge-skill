I just open-sourced something I've been building quietly — and I think it matters.

It's called the Islamic Knowledge Skill for Claude.

Here's the problem it solves:

Every day, millions of Muslims search for Islamic knowledge online.
They get blog posts with no citations.
They get social media posts with hadiths that were never said by the Prophet ﷺ.
They even get AI responses that sound authoritative — but hallucinate Islamic text entirely.

Falsely attributing words to the Prophet Muhammad ﷺ is one of the gravest errors in Islamic scholarship.
I couldn't sit with that problem and not try to solve it.

---

So I built an AI skill that does this differently.

It's a Claude skill backed by a real database — 20,972 records from three of the most authenticated sources in Islamic scholarship:

📖 The Holy Quran — 6,236 ayat, Saheeh International translation
📚 Sahih al-Bukhari — 7,277 hadiths across 97 books
📚 Sahih Muslim — 7,459 hadiths across 57 books

Bilingual. Arabic + English. Fully cited.

---

The key architectural decision: Claude never generates Islamic text from memory.

Every response queries a Supabase vector database.
The database returns exact, verbatim, unmodified text.
Claude presents it with the full citation: Surah:Ayah, or Book + Hadith number.

If something isn't in the database, it says so — and redirects to sunnah.com.

No AI-invented hadiths. No paraphrased ayat. The source, exactly as recorded.

---

What can it actually do?

→ A new Muslim asks how to perform Wudu at 3am — gets a step-by-step answer from Sahih Bukhari, cited
→ A professional asks what Islam says about business partnerships — gets the relevant trade hadiths instantly
→ Someone shares a viral "hadith" on social media — you can verify it in seconds against 14,736 authenticated records
→ A parent asks about the rights of parents in Islam — gets both the Quranic ayat AND the hadiths, together
→ An imam researching Friday's khutbah topic gets every relevant text across all three sources in one query

---

This serves every segment of 1.9 billion Muslims globally — and non-Muslims who want to understand what Islamic sources actually say, not what someone else says they say.

---

I built this as an AI transformation leader who believes technology has a responsibility in sensitive domains.

We talk a lot about AI for business efficiency.
We talk about AI for productivity and automation.

But AI can also serve knowledge preservation. Source integrity. Spiritual access.

This is open-source. Free. MIT licensed.
Anyone can fork it, improve it, build on it.

The next version will include the full Kutub al-Sittah — all six canonical hadith books.

---

If you're a Muslim developer, Islamic educator, da'wah worker, Islamic fintech builder, or just someone who wants authenticated Islamic knowledge on demand —

The repo is live. Link in the first comment.

بارك الله فيكم 🤍

---

#Islam #ArtificialIntelligence #OpenSource #IslamicKnowledge #AITransformation #Claude #Quran #Hadith #Dubai #TechForGood #IslamicFinance #MuslimProfessionals
