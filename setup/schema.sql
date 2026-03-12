-- ============================================================
-- Islamic Knowledge Skill — Supabase Schema
-- Author: Shady | github.com/shadyHassanin/islamic-knowledge-skill
-- ============================================================
-- Run this file in your Supabase SQL Editor before uploading data.
-- Enable pgvector extension first (Supabase Dashboard → Extensions → vector)
-- ============================================================

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- TABLE 1: Quran Verses
-- Source: quran-json (Saheeh International translation)
-- Records: 6,236 ayat across 114 surahs
-- ============================================================
CREATE TABLE IF NOT EXISTS quran_verses (
    id                  TEXT PRIMARY KEY,          -- Format: "surah:ayah" e.g. "2:255"
    surah_number        INTEGER NOT NULL,
    surah_name_arabic   TEXT NOT NULL,
    surah_name_english  TEXT NOT NULL,
    surah_transliteration TEXT NOT NULL,
    surah_type          TEXT NOT NULL,             -- 'meccan' or 'medinan'
    total_verses        INTEGER NOT NULL,
    ayah_number         INTEGER NOT NULL,
    arabic_text         TEXT NOT NULL,             -- Original Arabic — NEVER modified
    english_translation TEXT NOT NULL,             -- Saheeh International translation
    embedding           vector(1536),              -- For semantic search
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_quran_surah     ON quran_verses(surah_number);
CREATE INDEX IF NOT EXISTS idx_quran_ayah      ON quran_verses(surah_number, ayah_number);
CREATE INDEX IF NOT EXISTS idx_quran_type      ON quran_verses(surah_type);
CREATE INDEX IF NOT EXISTS idx_quran_embedding ON quran_verses USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================
-- TABLE 2: Sahih Bukhari Hadiths
-- Source: AhmedBaset/hadith-json
-- Records: 7,277 hadiths across 97 books
-- ============================================================
CREATE TABLE IF NOT EXISTS bukhari_hadiths (
    id                      INTEGER PRIMARY KEY,   -- Global hadith ID
    id_in_book              INTEGER NOT NULL,       -- Hadith number within the book
    book_id                 INTEGER NOT NULL,
    book_name_arabic        TEXT NOT NULL,
    book_name_english       TEXT NOT NULL,
    narrator                TEXT,                  -- Chain of narration (isnad)
    arabic_text             TEXT NOT NULL,         -- Original Arabic — NEVER modified
    english_text            TEXT NOT NULL,         -- English translation
    embedding               vector(1536),
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bukhari_book      ON bukhari_hadiths(book_id);
CREATE INDEX IF NOT EXISTS idx_bukhari_id_book   ON bukhari_hadiths(book_id, id_in_book);
CREATE INDEX IF NOT EXISTS idx_bukhari_embedding ON bukhari_hadiths USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================
-- TABLE 3: Sahih Muslim Hadiths
-- Source: AhmedBaset/hadith-json
-- Records: 7,459 hadiths across 57 books
-- ============================================================
CREATE TABLE IF NOT EXISTS muslim_hadiths (
    id                      INTEGER PRIMARY KEY,
    id_in_book              INTEGER NOT NULL,
    book_id                 INTEGER NOT NULL,
    book_name_arabic        TEXT NOT NULL,
    book_name_english       TEXT NOT NULL,
    arabic_text             TEXT NOT NULL,         -- Original Arabic — NEVER modified
    english_text            TEXT NOT NULL,
    embedding               vector(1536),
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_muslim_book      ON muslim_hadiths(book_id);
CREATE INDEX IF NOT EXISTS idx_muslim_id_book   ON muslim_hadiths(book_id, id_in_book);
CREATE INDEX IF NOT EXISTS idx_muslim_embedding ON muslim_hadiths USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================
-- RLS (Row Level Security) — Public read-only access
-- ============================================================
ALTER TABLE quran_verses    ENABLE ROW LEVEL SECURITY;
ALTER TABLE bukhari_hadiths ENABLE ROW LEVEL SECURITY;
ALTER TABLE muslim_hadiths  ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read access" ON quran_verses    FOR SELECT USING (true);
CREATE POLICY "Public read access" ON bukhari_hadiths FOR SELECT USING (true);
CREATE POLICY "Public read access" ON muslim_hadiths  FOR SELECT USING (true);

-- ============================================================
-- VERIFICATION QUERY — Run after upload to confirm record counts
-- Expected: quran=6236, bukhari=7277, muslim=7459, total=20972
-- ============================================================
-- SELECT
--     (SELECT COUNT(*) FROM quran_verses)    AS quran_count,
--     (SELECT COUNT(*) FROM bukhari_hadiths) AS bukhari_count,
--     (SELECT COUNT(*) FROM muslim_hadiths)  AS muslim_count,
--     (SELECT COUNT(*) FROM quran_verses) +
--     (SELECT COUNT(*) FROM bukhari_hadiths) +
--     (SELECT COUNT(*) FROM muslim_hadiths)  AS total_corpus;
