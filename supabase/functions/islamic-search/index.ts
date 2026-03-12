/**
 * Islamic Knowledge Skill — Supabase Edge Function
 * =================================================
 * Performs semantic vector search across all three Islamic text collections.
 * Returns exact, unmodified source text with full citation metadata.
 *
 * Deploy: supabase functions deploy islamic-search
 *
 * Author: Shady | github.com/shadyHassanin/islamic-knowledge-skill
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// ── Types ──────────────────────────────────────────────────────────────────────

interface SearchRequest {
  query: string;
  sources?: ("quran" | "bukhari" | "muslim")[];  // default: all three
  limit?: number;                                  // results per source, default: 5
  mode?: "semantic" | "exact";                    // default: semantic
  reference?: string;                             // e.g. "2:255" or "bukhari:1:1"
}

interface SearchResult {
  source: "quran" | "bukhari" | "muslim";
  citation: string;
  arabic_text: string;
  english_text: string;
  metadata: Record<string, unknown>;
  similarity?: number;
}

// ── Constants ──────────────────────────────────────────────────────────────────

const OPENAI_EMBED_URL = "https://api.openai.com/v1/embeddings";
const EMBED_MODEL      = "text-embedding-3-small";
const DEFAULT_LIMIT    = 5;
const MAX_LIMIT        = 20;

// ── Helpers ────────────────────────────────────────────────────────────────────

async function generateEmbedding(text: string): Promise<number[]> {
  const response = await fetch(OPENAI_EMBED_URL, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${Deno.env.get("OPENAI_API_KEY")}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ input: text, model: EMBED_MODEL }),
  });

  if (!response.ok) {
    throw new Error(`Embedding API error: ${response.status}`);
  }

  const data = await response.json();
  return data.data[0].embedding;
}

function formatCitation(source: string, record: Record<string, unknown>): string {
  if (source === "quran") {
    return `Quran ${record.surah_number}:${record.ayah_number} — ${record.surah_name_english} (${record.surah_transliteration})`;
  }
  if (source === "bukhari") {
    return `Sahih al-Bukhari — Book ${record.book_id}: ${record.book_name_english}, Hadith ${record.id_in_book}`;
  }
  return `Sahih Muslim — Book ${record.book_id}: ${record.book_name_english}, Hadith ${record.id_in_book}`;
}

// ── Exact Reference Lookup ─────────────────────────────────────────────────────

async function exactLookup(
  supabase: ReturnType<typeof createClient>,
  reference: string
): Promise<SearchResult | null> {

  // Quran: "2:255" format
  const quranMatch = reference.match(/^(\d+):(\d+)$/);
  if (quranMatch) {
    const { data } = await supabase
      .from("quran_verses")
      .select("*")
      .eq("surah_number", parseInt(quranMatch[1]))
      .eq("ayah_number", parseInt(quranMatch[2]))
      .single();

    if (data) {
      return {
        source: "quran",
        citation: formatCitation("quran", data),
        arabic_text: data.arabic_text,
        english_text: data.english_translation,
        metadata: {
          surah_name_arabic: data.surah_name_arabic,
          surah_type: data.surah_type,
          total_verses: data.total_verses,
        },
      };
    }
  }

  // Bukhari: "bukhari:book:hadith" format
  const bukhariMatch = reference.match(/^bukhari:(\d+):(\d+)$/i);
  if (bukhariMatch) {
    const { data } = await supabase
      .from("bukhari_hadiths")
      .select("*")
      .eq("book_id", parseInt(bukhariMatch[1]))
      .eq("id_in_book", parseInt(bukhariMatch[2]))
      .single();

    if (data) {
      return {
        source: "bukhari",
        citation: formatCitation("bukhari", data),
        arabic_text: data.arabic_text,
        english_text: data.narrator ? `${data.narrator} ${data.english_text}` : data.english_text,
        metadata: { book_name_arabic: data.book_name_arabic },
      };
    }
  }

  // Muslim: "muslim:book:hadith" format
  const muslimMatch = reference.match(/^muslim:(\d+):(\d+)$/i);
  if (muslimMatch) {
    const { data } = await supabase
      .from("muslim_hadiths")
      .select("*")
      .eq("book_id", parseInt(muslimMatch[1]))
      .eq("id_in_book", parseInt(muslimMatch[2]))
      .single();

    if (data) {
      return {
        source: "muslim",
        citation: formatCitation("muslim", data),
        arabic_text: data.arabic_text,
        english_text: data.english_text,
        metadata: { book_name_arabic: data.book_name_arabic },
      };
    }
  }

  return null;
}

// ── Semantic Search ────────────────────────────────────────────────────────────

async function semanticSearch(
  supabase: ReturnType<typeof createClient>,
  embedding: number[],
  sources: string[],
  limit: number
): Promise<SearchResult[]> {

  const results: SearchResult[] = [];
  const embeddingStr = `[${embedding.join(",")}]`;

  // Search Quran
  if (sources.includes("quran")) {
    const { data } = await supabase.rpc("search_quran", {
      query_embedding: embeddingStr,
      match_count: limit,
    });

    (data || []).forEach((row: Record<string, unknown>) => {
      results.push({
        source: "quran",
        citation: formatCitation("quran", row),
        arabic_text: row.arabic_text as string,
        english_text: row.english_translation as string,
        metadata: {
          surah_name_arabic: row.surah_name_arabic,
          surah_type: row.surah_type,
        },
        similarity: row.similarity as number,
      });
    });
  }

  // Search Bukhari
  if (sources.includes("bukhari")) {
    const { data } = await supabase.rpc("search_bukhari", {
      query_embedding: embeddingStr,
      match_count: limit,
    });

    (data || []).forEach((row: Record<string, unknown>) => {
      const narrator = row.narrator as string;
      results.push({
        source: "bukhari",
        citation: formatCitation("bukhari", row),
        arabic_text: row.arabic_text as string,
        english_text: narrator ? `${narrator} ${row.english_text}` : row.english_text as string,
        metadata: { book_name_arabic: row.book_name_arabic },
        similarity: row.similarity as number,
      });
    });
  }

  // Search Muslim
  if (sources.includes("muslim")) {
    const { data } = await supabase.rpc("search_muslim", {
      query_embedding: embeddingStr,
      match_count: limit,
    });

    (data || []).forEach((row: Record<string, unknown>) => {
      results.push({
        source: "muslim",
        citation: formatCitation("muslim", row),
        arabic_text: row.arabic_text as string,
        english_text: row.english_text as string,
        metadata: { book_name_arabic: row.book_name_arabic },
        similarity: row.similarity as number,
      });
    });
  }

  // Sort all results by similarity score across sources
  return results.sort((a, b) => (b.similarity || 0) - (a.similarity || 0));
}

// ── Main Handler ───────────────────────────────────────────────────────────────

serve(async (req: Request) => {
  // CORS
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
      },
    });
  }

  try {
    const body: SearchRequest = await req.json();
    const {
      query,
      sources = ["quran", "bukhari", "muslim"],
      limit   = DEFAULT_LIMIT,
      mode    = "semantic",
      reference,
    } = body;

    if (!query && !reference) {
      return new Response(
        JSON.stringify({ error: "Either 'query' or 'reference' is required" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
    );

    const actualLimit = Math.min(limit, MAX_LIMIT);
    let results: SearchResult[] = [];

    // Exact reference lookup takes priority
    if (reference) {
      const result = await exactLookup(supabase, reference);
      if (result) {
        results = [result];
      } else {
        return new Response(
          JSON.stringify({
            results: [],
            message: "Reference not found in the authenticated dataset. Please verify at sunnah.com or quran.com.",
            query: reference,
          }),
          { headers: { "Content-Type": "application/json" } }
        );
      }
    } else {
      // Semantic search
      const embedding = await generateEmbedding(query);
      results = await semanticSearch(supabase, embedding, sources, actualLimit);
    }

    return new Response(
      JSON.stringify({
        results,
        total: results.length,
        sources_searched: sources,
        query: query || reference,
        // Critical integrity notice included in every response
        integrity_notice: "All text returned verbatim from authenticated datasets. No AI-generated hadith text.",
      }),
      { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } }
    );

  } catch (error) {
    console.error("Search error:", error);
    return new Response(
      JSON.stringify({ error: "Search failed. Please try again." }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});
