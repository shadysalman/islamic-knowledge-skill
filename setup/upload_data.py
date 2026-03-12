"""
Islamic Knowledge Skill — Data Upload Pipeline
===============================================
Uploads Quran, Sahih Bukhari, and Sahih Muslim to Supabase.
Generates vector embeddings for semantic search.

Author: Shady | github.com/shadyHassanin/islamic-knowledge-skill

Prerequisites:
    pip install -r requirements.txt

Usage:
    python upload_data.py --supabase-url YOUR_URL --supabase-key YOUR_SERVICE_KEY

Data files required (see data/README.md for download links):
    data/quran_en.json
    data/bukhari.json
    data/muslim.json
"""

import json
import time
import argparse
import sys
from pathlib import Path

try:
    from supabase import create_client, Client
    from openai import OpenAI
    from tqdm import tqdm
except ImportError:
    print("Missing dependencies. Run: pip install -r requirements.txt")
    sys.exit(1)


# ── Configuration ──────────────────────────────────────────────────────────────

BATCH_SIZE = 50          # Records per Supabase insert batch
EMBED_BATCH = 20         # Records per embedding API call
EMBED_MODEL = "text-embedding-3-small"   # OpenAI embedding model (1536 dims)
DATA_DIR = Path(__file__).parent.parent / "data"


# ── Helpers ────────────────────────────────────────────────────────────────────

def get_embedding(client: OpenAI, texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts."""
    response = client.embeddings.create(
        input=texts,
        model=EMBED_MODEL
    )
    return [item.embedding for item in response.data]


def batch_insert(supabase: Client, table: str, records: list[dict], desc: str):
    """Insert records in batches with progress tracking."""
    total = len(records)
    inserted = 0
    errors = 0

    for i in tqdm(range(0, total, BATCH_SIZE), desc=f"Uploading {desc}"):
        batch = records[i:i + BATCH_SIZE]
        try:
            supabase.table(table).upsert(batch).execute()
            inserted += len(batch)
        except Exception as e:
            errors += len(batch)
            print(f"\n  Error in batch {i//BATCH_SIZE}: {e}")
        time.sleep(0.05)  # Respect rate limits

    print(f"  {desc}: {inserted} inserted, {errors} errors")
    return inserted


# ── Quran Upload ───────────────────────────────────────────────────────────────

def upload_quran(supabase: Client, openai_client: OpenAI):
    print("\n── Quran ──────────────────────────────────────")

    path = DATA_DIR / "quran_en.json"
    if not path.exists():
        print(f"  ERROR: {path} not found. See data/README.md")
        return 0

    with open(path, encoding="utf-8") as f:
        quran = json.load(f)

    records = []
    texts_for_embedding = []

    for surah in quran:
        for verse in surah["verses"]:
            record_id = f"{surah['id']}:{verse['id']}"
            embed_text = f"Surah {surah['transliteration']} {surah['id']}:{verse['id']} — {verse['translation']}"

            records.append({
                "id":                   record_id,
                "surah_number":         surah["id"],
                "surah_name_arabic":    surah["name"],
                "surah_name_english":   surah["translation"],
                "surah_transliteration": surah["transliteration"],
                "surah_type":           surah["type"],
                "total_verses":         surah["total_verses"],
                "ayah_number":          verse["id"],
                "arabic_text":          verse["text"],
                "english_translation":  verse["translation"],
                "embedding":            None   # filled below
            })
            texts_for_embedding.append(embed_text)

    # Generate embeddings in batches
    print(f"  Generating embeddings for {len(records)} verses...")
    embeddings = []
    for i in tqdm(range(0, len(texts_for_embedding), EMBED_BATCH), desc="  Embedding"):
        batch = texts_for_embedding[i:i + EMBED_BATCH]
        embeddings.extend(get_embedding(openai_client, batch))
        time.sleep(0.1)

    for i, record in enumerate(records):
        record["embedding"] = embeddings[i]

    return batch_insert(supabase, "quran_verses", records, "Quran verses")


# ── Sahih Bukhari Upload ───────────────────────────────────────────────────────

def upload_bukhari(supabase: Client, openai_client: OpenAI):
    print("\n── Sahih Bukhari ──────────────────────────────")

    path = DATA_DIR / "bukhari.json"
    if not path.exists():
        print(f"  ERROR: {path} not found. See data/README.md")
        return 0

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Build chapter lookup
    chapter_lookup = {ch["id"]: ch for ch in data["chapters"]}
    records = []
    texts_for_embedding = []

    for hadith in data["hadiths"]:
        chapter = chapter_lookup.get(hadith["chapterId"], {})
        english_text = hadith["english"].get("text", "") if isinstance(hadith["english"], dict) else ""
        narrator = hadith["english"].get("narrator", "") if isinstance(hadith["english"], dict) else ""
        arabic_text = hadith.get("arabic", "")

        if not english_text:
            continue

        embed_text = f"Sahih Bukhari Book {hadith['bookId']} Hadith {hadith['idInBook']} — {narrator} {english_text[:300]}"

        records.append({
            "id":                hadith["id"],
            "id_in_book":        hadith["idInBook"],
            "book_id":           hadith["bookId"],
            "book_name_arabic":  chapter.get("arabic", ""),
            "book_name_english": chapter.get("english", ""),
            "narrator":          narrator,
            "arabic_text":       arabic_text,
            "english_text":      english_text,
            "embedding":         None
        })
        texts_for_embedding.append(embed_text)

    print(f"  Generating embeddings for {len(records)} hadiths...")
    embeddings = []
    for i in tqdm(range(0, len(texts_for_embedding), EMBED_BATCH), desc="  Embedding"):
        batch = texts_for_embedding[i:i + EMBED_BATCH]
        embeddings.extend(get_embedding(openai_client, batch))
        time.sleep(0.1)

    for i, record in enumerate(records):
        record["embedding"] = embeddings[i]

    return batch_insert(supabase, "bukhari_hadiths", records, "Bukhari hadiths")


# ── Sahih Muslim Upload ────────────────────────────────────────────────────────

def upload_muslim(supabase: Client, openai_client: OpenAI):
    print("\n── Sahih Muslim ───────────────────────────────")

    path = DATA_DIR / "muslim.json"
    if not path.exists():
        print(f"  ERROR: {path} not found. See data/README.md")
        return 0

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    chapter_lookup = {ch["id"]: ch for ch in data["chapters"]}
    records = []
    texts_for_embedding = []

    for hadith in data["hadiths"]:
        chapter = chapter_lookup.get(hadith["chapterId"], {})
        english_text = hadith["english"].get("text", "") if isinstance(hadith["english"], dict) else ""
        arabic_text = hadith.get("arabic", "")

        if not english_text:
            continue

        embed_text = f"Sahih Muslim Book {hadith['bookId']} Hadith {hadith['idInBook']} — {english_text[:300]}"

        records.append({
            "id":                hadith["id"],
            "id_in_book":        hadith["idInBook"],
            "book_id":           hadith["bookId"],
            "book_name_arabic":  chapter.get("arabic", ""),
            "book_name_english": chapter.get("english", ""),
            "arabic_text":       arabic_text,
            "english_text":      english_text,
            "embedding":         None
        })
        texts_for_embedding.append(embed_text)

    print(f"  Generating embeddings for {len(records)} hadiths...")
    embeddings = []
    for i in tqdm(range(0, len(texts_for_embedding), EMBED_BATCH), desc="  Embedding"):
        batch = texts_for_embedding[i:i + EMBED_BATCH]
        embeddings.extend(get_embedding(openai_client, batch))
        time.sleep(0.1)

    for i, record in enumerate(records):
        record["embedding"] = embeddings[i]

    return batch_insert(supabase, "muslim_hadiths", records, "Muslim hadiths")


# ── Verification ───────────────────────────────────────────────────────────────

def verify_counts(supabase: Client):
    print("\n── Verification ───────────────────────────────")
    quran_count   = supabase.table("quran_verses").select("id", count="exact").execute().count
    bukhari_count = supabase.table("bukhari_hadiths").select("id", count="exact").execute().count
    muslim_count  = supabase.table("muslim_hadiths").select("id", count="exact").execute().count
    total         = (quran_count or 0) + (bukhari_count or 0) + (muslim_count or 0)

    print(f"  Quran verses:     {quran_count:,}   (expected: 6,236)")
    print(f"  Bukhari hadiths:  {bukhari_count:,}  (expected: 7,277)")
    print(f"  Muslim hadiths:   {muslim_count:,}  (expected: 7,459)")
    print(f"  ─────────────────────────────────────")
    print(f"  Total corpus:     {total:,}  (expected: 20,972)")

    if total == 20972:
        print("\n  ✓ All records verified. Dataset integrity confirmed.")
    else:
        print(f"\n  ⚠ Count mismatch. Expected 20,972, got {total:,}. Review errors above.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Upload Islamic knowledge datasets to Supabase")
    parser.add_argument("--supabase-url",  required=True, help="Supabase project URL")
    parser.add_argument("--supabase-key",  required=True, help="Supabase service role key")
    parser.add_argument("--openai-key",    required=True, help="OpenAI API key (for embeddings)")
    parser.add_argument("--source",        default="all",  help="all | quran | bukhari | muslim")
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════╗")
    print("║  Islamic Knowledge Skill — Data Pipeline     ║")
    print("║  Corpus: Quran + Bukhari + Muslim            ║")
    print("╚══════════════════════════════════════════════╝")

    supabase     = create_client(args.supabase_url, args.supabase_key)
    openai_client = OpenAI(api_key=args.openai_key)

    source = args.source.lower()

    if source in ("all", "quran"):
        upload_quran(supabase, openai_client)
    if source in ("all", "bukhari"):
        upload_bukhari(supabase, openai_client)
    if source in ("all", "muslim"):
        upload_muslim(supabase, openai_client)

    verify_counts(supabase)
    print("\n  Done. Your Islamic knowledge database is ready.\n")


if __name__ == "__main__":
    main()
