import os
import json
import re
import logging
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

VALID_ROLES = {
    "title", "author", "affiliation", "abstract", "abstract_heading",
    "keywords", "keywords_heading", "section_heading", "sub_heading",
    "body", "reference", "figure_caption", "table_caption", "equation",
}

# ── Model selection ──────────────────────────────────────────────────────────
# llama-3.1-8b-instant: too small for layout-aware classification.
# llama-3.3-70b-versatile: best accuracy/cost trade-off on Groq as of Mar 2026.
# llama3-70b-8192 is the fallback if 3.3 is rate-limited or unavailable.
_MODEL_PRIMARY  = "llama-3.3-70b-versatile"
_MODEL_FALLBACK = "llama3-70b-8192"

# Roles the parser assigns with near-certainty via regex / style rules.
# The LLM never sees these — saves tokens and prevents second-guessing.
HIGH_CONFIDENCE_ROLES = {"title", "reference", "section_heading", "sub_heading"}

# Max paragraphs forwarded as context. 70b handles ~4k tokens comfortably;
# 60 paragraph lines ≈ 1.5k tokens, leaving room for prompt overhead.
_MAX_BATCH_SIZE = 60

class ContentClassifier:
    """
    ONLY corrects paragraph roles using Groq.
    Does NOT build title/authors/sections/etc. — that is mapper's job.
    """

    def __init__(self, env_path: str | Path = None):
        self._load_api_key(env_path)

    def classify(self, parser_output: dict[str, Any]) -> dict[str, Any]:
        raw_paragraphs = parser_output.get("raw_paragraphs", [])

        if not raw_paragraphs:
            logger.warning("No paragraphs found.")
            return {**parser_output, "classification_meta": self._empty_meta()}

        high_conf, ambiguous = self._split_by_confidence(raw_paragraphs)
        logger.info(f"Total: {len(raw_paragraphs)} | High-conf: {len(high_conf)} | Ambiguous: {len(ambiguous)}")

        corrections = {}
        if ambiguous:
            corrections = self._classify_with_groq(ambiguous, raw_paragraphs)

        corrected_paragraphs, changes = self._apply_corrections(raw_paragraphs, corrections)

        updated_output = {**parser_output}
        updated_output["raw_paragraphs"] = corrected_paragraphs

        updated_output["classification_meta"] = {
            "total_paragraphs": len(raw_paragraphs),
            "high_confidence_kept": len(high_conf),
            "ambiguous_sent": len(ambiguous),
            "corrections_made": len(changes),
            "changes": changes,
            "model_used": corrections.get("_model_used", _MODEL_PRIMARY),
            "fallback_used": corrections.get("_fallback", False),
        }

        return updated_output

    def _split_by_confidence(self, paragraphs: list[dict]):
        high = [p for p in paragraphs if p["role"] in HIGH_CONFIDENCE_ROLES]
        amb = [p for p in paragraphs if p["role"] not in HIGH_CONFIDENCE_ROLES]
        return high, amb

    def _classify_with_groq(self, ambiguous: list[dict], all_paras: list[dict]) -> dict:
        """
        Calls Groq with primary model; retries once with fallback model on failure.
        Returns a dict of {paragraph_index: new_role, ...} plus internal keys.
        If no GROQ_API_KEY is configured, runs in no-LLM mode and returns
        an empty corrections dict with fallback metadata.
        """
        # No-LLM fallback: run without external API instead of raising
        if not getattr(self, "_api_key", None):
            logger.warning("GROQ_API_KEY missing; skipping LLM classification (no-LLM mode).")
            return {"_fallback": True, "_model_used": None}

        for model in (_MODEL_PRIMARY, _MODEL_FALLBACK):
            try:
                prompt = self._build_prompt(ambiguous, all_paras)
                raw_text = self._query_groq(prompt, model=model)
                corrections = self._parse_llm_response(raw_text, ambiguous)
                corrections["_model_used"] = model
                corrections["_fallback"] = model != _MODEL_PRIMARY
                return corrections
            except Exception as e:
                logger.warning(f"Model {model} failed: {e}")

        logger.error("All models failed — using fallback (no corrections).")
        return {"_fallback": True, "_model_used": _MODEL_FALLBACK}

    def _query_groq(self, prompt: str, model: str = _MODEL_PRIMARY) -> str:
        if not hasattr(self, "_api_key") or not self._api_key:
            raise EnvironmentError("GROQ_API_KEY missing in .env")

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a precise academic document structure classifier. "
                        "You MUST return ONLY a valid JSON object — no prose, no markdown, "
                        "no code fences, no explanation. "
                        "If you output anything other than a JSON object the response is invalid."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1024,   # role corrections are short; 2000 was wasteful
            "temperature": 0.0,   # deterministic — no creativity needed
            "top_p": 0.1,         # further tightens distribution around top token
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=45)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    def _build_prompt(self, ambiguous: list[dict], all_paragraphs: list[dict]) -> str:
        """
        Builds the classification prompt sent to the LLM.

        Design principles:
        - Full document shown as context so the model has positional awareness
          (e.g. knows [05] is "after keywords" → must be section_heading).
        - Ambiguous indices listed explicitly — model only changes those.
        - Concrete examples for every tricky boundary case.
        - Short, column-aligned context lines → low token cost, high readability.
        - "If unsure, keep original" instruction reduces hallucinated role changes.
        """
        # ── Context block ──────────────────────────────────────────────────
        context_lines = []
        for p in all_paragraphs[:_MAX_BATCH_SIZE]:
            props  = p.get("ooxml_properties", {})
            sz     = str(props.get("size_pt", "?"))
            bold   = "B" if props.get("bold") else " "
            italic = "I" if props.get("italic") else " "
            align  = props.get("alignment", "?")[:1].upper()  # L/C/R/B(oth)
            text   = p["text"][:90]
            line = (
                f"[{p['index']:02d}] {p['role']:20s} "
                f"sz={sz:4s} {bold}{italic}{align} | {text}"
            )
            context_lines.append(line)

        context_block     = "\n".join(context_lines)
        ambiguous_indices = [p["index"] for p in ambiguous[:_MAX_BATCH_SIZE]]
        ambiguous_str     = ", ".join(str(i) for i in ambiguous_indices)

        prompt = f"""
=== DOCUMENT PARAGRAPHS (full context, do NOT change roles not in TARGET list) ===
Format: [idx] current_role   sz bold/italic/align | text

{context_block}

=== YOUR TASK ===
Re-classify ONLY these paragraph indices: {ambiguous_str}

Return a JSON object mapping index (as string) → corrected role.
- Include an index ONLY if you are CHANGING its role.
- If you are unsure, keep the original role (omit from output).
- Empty object {{}} is valid if nothing needs changing.

=== VALID ROLES (use exactly these strings) ===
title | author | affiliation | abstract | abstract_heading |
keywords | keywords_heading | section_heading | sub_heading |
body | reference | figure_caption | table_caption | equation

=== ROLE DECISION GUIDE (read carefully before classifying) ===

TITLE
  ✔ First paragraph of the document, large/bold, describes the paper topic.
  ✔ "Deep Reinforcement Learning for Multi-Agent Cooperative Tasks"
  ✘ A section heading like "I. INTRODUCTION" is section_heading, not title.

AUTHOR vs AFFILIATION vs BODY
  author      → Person name(s) only. Often has superscript numbers (¹²³).
                "Rahul Sharma¹"   "Jane Doe², Carlos Mendes³"
  affiliation → Institution, department, city, country, email.
                "¹Dept. of CS, IIT Delhi, India"   "²MIT CSAIL, Cambridge, USA"
                "rahul@iitd.ac.in"
  body        → Full sentence of scientific content. Never just a name or institution.
  KEY: A line with a person's name AND an institution on the same line
       → split mentally: treat as author (name carries more weight).

ABSTRACT vs ABSTRACT_HEADING
  abstract         → Full abstract text, possibly starting with "Abstract—".
                     "Abstract—Cooperative target tracking has emerged..."
  abstract_heading → The standalone word "Abstract" or "ABSTRACT" alone,
                     with no body text on the same line.
                     "Abstract"   "ABSTRACT"

KEYWORDS vs KEYWORDS_HEADING
  keywords         → Full keywords line, possibly starting with "Keywords—".
                     "Keywords—Multi-UAV, MARL, cooperative tracking"
  keywords_heading → Standalone label only: "Keywords" / "Index Terms"

SECTION_HEADING vs SUB_HEADING
  section_heading → Roman numeral prefix OR standalone ALL-CAPS known heading.
                    "I. INTRODUCTION"   "II. RELATED WORK"   "CONCLUSION"
  sub_heading     → Numeric (3.1) or alpha (A.) prefix, max ~8 words.
                    "3.1 Observation Space"   "A. Network Architecture"
  KEY: "I. INTRODUCTION" is section_heading even without formatting.
       "3.1 Observation Space" is sub_heading even if it looks bold.

TABLE_CAPTION vs BOLD BODY LINE
  table_caption  → Starts with TABLE + Roman/Arabic numeral (with dot/colon).
                   "TABLE I. TRACKING PERFORMANCE"   "Table 2: Ablation Study"
  figure_caption → Starts with Fig./Figure + numeral.
                   "Fig. 3. System architecture overview."
  body           → Any bold line that is NOT a table/figure label.

REFERENCE
  reference → Bibliographic entry. Starts with [N] or "N." followed by author.
              "[1] J. N. Foerster et al., ..."   "1. Smith, J. (2020)..."
  KEY: already-labelled references are HIGH-CONFIDENCE and will NOT appear
       in the TARGET list. Only re-label body/author lines that look like refs.

=== OUTPUT FORMAT ===
Return ONLY a JSON object. No prose. No markdown. No code fences.
Correct example:  {{"3": "affiliation", "7": "abstract", "11": "keywords"}}
Empty example:    {{}}
"""
        return prompt.strip()

    def _parse_llm_response(self, raw_text: str, ambiguous: list[dict]) -> dict:
        """
        Robustly extracts {index: role} corrections from LLM output.

        Tries four strategies in order of strictness:
          1. Direct json.loads on cleaned text  (ideal case)
          2. Extract first {...} block via regex (model added prose around JSON)
          3. Fix common JSON errors then parse   (missing quotes, trailing commas)
          4. Line-by-line key:value extraction   (model returned non-JSON format)

        Any index not in the ambiguous set is silently discarded.
        Any role string not in VALID_ROLES is silently discarded.
        """
        # Build a lookup set for fast validation
        ambiguous_idx_set = {p["index"] for p in ambiguous}

        def _validate(parsed: dict) -> dict:
            """Keep only valid index→role pairs within the ambiguous set."""
            out = {}
            for k, v in parsed.items():
                # Key: accept int or string integer
                try:
                    idx = int(str(k).strip())
                except (ValueError, TypeError):
                    continue
                if idx not in ambiguous_idx_set:
                    continue
                # Value: must be a recognised role string
                role = str(v).strip().lower().replace("-", "_")
                if role in VALID_ROLES:
                    out[idx] = role
            return out

        # ── Strategy 1: clean and direct parse ────────────────────────────
        cleaned = raw_text.strip()
        # Strip markdown code fences (```json ... ``` or ``` ... ```)
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$",          "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                result = _validate(parsed)
                logger.debug(f"Strategy 1 succeeded: {len(result)} corrections")
                return result
        except json.JSONDecodeError:
            pass

        # ── Strategy 2: extract first {...} block ─────────────────────────
        # Handles: "Here are the corrections: {...} Hope that helps!"
        brace_match = re.search(r"\{[^{}]*\}", cleaned, re.DOTALL)
        if brace_match:
            try:
                parsed = json.loads(brace_match.group())
                if isinstance(parsed, dict):
                    result = _validate(parsed)
                    logger.debug(f"Strategy 2 succeeded: {len(result)} corrections")
                    return result
            except json.JSONDecodeError:
                pass

        # ── Strategy 3: repair common JSON errors and retry ───────────────
        repaired = cleaned
        # Fix single-quoted strings: {'5': 'abstract'} → {"5": "abstract"}
        repaired = re.sub(r"'([^']*)'", r'"\1"', repaired)
        # Fix unquoted string values: {5: abstract} → {"5": "abstract"}
        repaired = re.sub(
            r'(\{|,)\s*(\d+)\s*:\s*([a-z_]+)',
            r'\1"\2": "\3"',
            repaired,
        )
        # Remove trailing commas before } or ]
        repaired = re.sub(r",\s*([}\]])", r"\1", repaired)

        try:
            parsed = json.loads(repaired)
            if isinstance(parsed, dict):
                result = _validate(parsed)
                logger.debug(f"Strategy 3 (repaired) succeeded: {len(result)} corrections")
                return result
        except json.JSONDecodeError:
            pass

        # ── Strategy 4: line-by-line key:value scan ───────────────────────
        # Handles responses like:
        #   3: affiliation
        #   "7": "abstract"
        #   index 11 → keywords
        result = {}
        for line in cleaned.splitlines():
            # Match: optional quote, digits, optional quote, separator, role
            m = re.search(
                r'"?(\d+)"?\s*[:→\-]+\s*"?([a-z_]+)"?',
                line,
                re.IGNORECASE,
            )
            if m:
                try:
                    idx  = int(m.group(1))
                    role = m.group(2).strip().lower()
                    if idx in ambiguous_idx_set and role in VALID_ROLES:
                        result[idx] = role
                except (ValueError, TypeError):
                    continue

        if result:
            logger.debug(f"Strategy 4 (line scan) succeeded: {len(result)} corrections")
            return result

        # ── All strategies failed ─────────────────────────────────────────
        logger.warning(
            f"_parse_llm_response: all strategies failed.\n"
            f"Raw response (first 400 chars):\n{raw_text[:400]}"
        )
        return {}

    def _apply_corrections(self, paragraphs: list[dict], corrections: dict):
        changes = []
        corrected = []
        for p in paragraphs:
            p_copy = dict(p)
            idx = p["index"]
            if idx in corrections:
                old = p["role"]
                new = corrections[idx]
                if old != new:
                    p_copy["role"] = new
                    changes.append({"index": idx, "old_role": old, "new_role": new, "text": p["text"][:60]})
            corrected.append(p_copy)
        return corrected, changes

    def _load_api_key(self, env_path=None):
        # Prefer an explicit env_path if provided, otherwise fall back to default
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()

        key = os.getenv("GROQ_API_KEY")
        if not key:
            logger.warning("GROQ_API_KEY not found in environment; running classifier in no-LLM mode.")
            self._api_key = None
            return

        self._api_key = key

    @staticmethod
    def _empty_meta():
        return {
            "total_paragraphs": 0,
            "high_confidence_kept": 0,
            "ambiguous_sent": 0,
            "corrections_made": 0,
            "changes": [],
            "model_used": _MODEL_PRIMARY,
            "fallback_used": False,
        }


# ── Test ────────────────────────────────────────
if __name__ == "__main__":
    path = r"D:\DATA SCIENCE AND ML\Project\ManuscriptMagic.AI\template\test.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    clf = ContentClassifier()
    result = clf.classify(data)

    print("Classification complete!")
    print(f"Corrections made: {len(result['classification_meta']['changes'])}")
    for ch in result['classification_meta']['changes']:
        print(f"  [{ch['index']}] {ch['old_role']} → {ch['new_role']}")