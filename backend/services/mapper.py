"""
mapper.py — ContentMapper
==========================
Maps classifier output → clean structured schema for TemplateFormatter.

Bug fixes in this version (all verified against test.json forensics)
─────────────────────────────────────────────────────────────────────
BUG-1  _extract_authors():
       Old: checked role=="author" and skipped text=="AUTHORS".
            Author names sit in role=body paragraphs (para[03], [04]) → authors=[].
       Fix: enter an "author block" when the AUTHORS label is seen; collect
            the NEXT body paragraphs; split each into name + affiliation.

BUG-2  _extract_affiliations():
       Old: keyword-scanned the ENTIRE document with no positional boundary.
            Matched abstract [06], open-source sentence [16], conclusion [50].
       Fix: affiliations extracted in the SAME positional pass as authors
            (single method _extract_authors_and_affiliations).  Stops at
            abstract_heading so nothing outside the author block leaks in.

BUG-3  _extract_keywords():
       Old: "Large Language Models" in text matched para[01]=title first
            → keywords = title text.
       Fix: walk forward only from the keywords_heading / keywords_role node.

BUG-4  _extract_acknowledgments():
       Old: "acknowledg" in text matched para[51]=section_heading "ACKNOWLEDGMENTS"
            → returned the heading label as ack text.
       Fix: enter collection state on the heading; collect the BODY paragraph(s)
            that follow it, not the heading itself.

BUG-5  _extract_sections_fixed():
       Old: ALL-CAPS regex ^[A-Z][A-Z\s&]+$ caught TITLE / AUTHORS / ABSTRACT /
            KEYWORDS labels → all four appeared as numbered body sections I–IV.
       Fix: hard-filter set _STRUCTURAL_HEADINGS excludes them before any section
            is appended.

BUG-6  _extract_sections_fixed() — fused section labels:
       Old: "RELATED WORK Early attempts...", "PROPOSED METHODOLOGY 3.1 ...",
            "EXPERIMENTAL SETUP 4.1 ..." had role=body and were never promoted
            to section headings → three body sections were missing.
       Fix: _CAPS_PREFIX_RE regex detects an ALL-CAPS label at the start of a
            body paragraph; if the label is in _CAPS_SECTION_LABELS the label
            becomes the heading and the remainder becomes the first content item.
"""

import json
import re
from datetime import datetime
from pathlib import Path


# ── Constants ─────────────────────────────────────────────────────────────────

# Headings that belong to the header zone — must NEVER appear as numbered sections
_STRUCTURAL_HEADINGS = {
    "TITLE", "AUTHORS", "AUTHOR",
    "ABSTRACT",
    "KEYWORDS", "KEYWORD", "INDEX TERMS",
    "REFERENCES", "BIBLIOGRAPHY",
    "ACKNOWLEDGMENT", "ACKNOWLEDGMENTS", "ACKNOWLEDGEMENTS",
}

# Known ALL-CAPS section labels that the parser fuses into body paragraphs (BUG-6)
_CAPS_SECTION_LABELS = {
    "INTRODUCTION",
    "RELATED WORK", "BACKGROUND", "LITERATURE REVIEW",
    "METHODOLOGY", "METHOD", "METHODS", "APPROACH",
    "PROPOSED METHOD", "PROPOSED METHODOLOGY",
    "EXPERIMENTAL SETUP", "EXPERIMENTS", "EXPERIMENTAL RESULTS",
    "RESULTS", "RESULTS AND DISCUSSION",
    "DISCUSSION", "ANALYSIS", "EVALUATION",
    "CONCLUSION", "CONCLUSIONS", "FUTURE WORK",
    "CONCLUSION AND FUTURE WORK",
}

# Known heading names used for section detection (mirrors parser.py set)
_KNOWN_HEADINGS_UPPER = {s.upper() for s in {
    "abstract", "introduction", "related work", "background",
    "literature review", "methodology", "methods", "approach",
    "proposed method", "system design", "architecture",
    "experimental results", "experiments", "results",
    "results and discussion", "discussion", "analysis",
    "evaluation", "conclusion", "conclusions",
    "future work", "conclusion and future work",
    "acknowledgment", "acknowledgements", "acknowledgments",
    "references", "bibliography",
}}

# Affiliation-signal words — only tested WITHIN the author block (BUG-2)
_AFF_WORDS = {
    "university", "institute", "department", "dept", "college",
    "laboratory", "lab", "centre", "center", "school", "faculty",
    "professor", "assistant", "iit", "nit", "iisc",
    "hospital", "corporation", "corp", "ltd", "research",
}
_AFF_SUBSTRS = {"@", ".edu", ".ac.", ".org", ".gov"}

# Detects ALL-CAPS label at the very start of a body paragraph (BUG-6)
# "RELATED WORK Early attempts..." → group(1) = "RELATED WORK"
_CAPS_PREFIX_RE = re.compile(
    r"^([A-Z][A-Z\s&]{2,35}?)\s{1,3}(?=[A-Z][a-z]|\d)"
)


# ── ContentMapper ─────────────────────────────────────────────────────────────

class ContentMapper:

    def __init__(self, ieee_spec_path: str):
        self.spec_path = Path(ieee_spec_path)
        with open(self.spec_path, "r", encoding="utf-8") as f:
            self._full_spec = json.load(f)
        self._styles = self._full_spec.get("styles", {})

    # ── Public API ─────────────────────────────────────────────────────────────

    def map_content(self, classifier_output: dict) -> dict:
        paragraphs = classifier_output.get("raw_paragraphs", [])

        # BUG-1 + BUG-2: single positional pass for both authors and affiliations
        authors, affiliations = self._extract_authors_and_affiliations(paragraphs)

        structured = {
            "title":           self._extract_title(paragraphs),
            "authors":         authors,
            "affiliations":    affiliations,
            "abstract":        self._extract_abstract(paragraphs),
            "keywords":        self._extract_keywords(paragraphs),       # BUG-3
            "sections":        self._extract_sections(paragraphs),       # BUG-5 + BUG-6
            "references":      self._extract_references(paragraphs),
            "acknowledgments": self._extract_acknowledgments(paragraphs), # BUG-4
            "tables":          classifier_output.get("tables", []),
        }

        # New: Extract text-based tables from section bodies
        text_tables = self._extract_tables_from_text(structured["sections"])
        structured["tables"].extend(text_tables)

        mapped_paras = [
            {**p, **self._validate_paragraph(p)} for p in paragraphs
        ]

        return {
            "metadata": {
                "source_file": (
                    classifier_output.get("source_file")
                    or classifier_output.get("metadata", {}).get("source_file", "unknown")
                ),
                "paragraph_count":    len(paragraphs),
                "valid_paragraphs":   sum(1 for p in mapped_paras if p.get("is_valid", True)),
                "invalid_paragraphs": sum(1 for p in mapped_paras if not p.get("is_valid", True)),
                "total_violations":   sum(len(p.get("violations", {})) for p in mapped_paras),
                "timestamp":          datetime.now().isoformat(),
            },
            **structured,
            "paragraphs":        mapped_paras,
            "violation_summary": {"by_property": {}, "by_style": {}},
        }

    def validate_mapping(self, mapped_content: dict) -> list:
        issues = []
        if not mapped_content.get("title"):
            issues.append("Missing title")
        if not mapped_content.get("abstract"):
            issues.append("Missing abstract")
        if not mapped_content.get("sections"):
            issues.append("No body sections found")
        return issues

    # ── Title ──────────────────────────────────────────────────────────────────

    def _extract_title(self, paras: list) -> str:
        """
        Parser emits: [role=title, text="TITLE"] → [role=body, text="<actual title>"]
        Walk forward from the title node to find real content.
        """
        for i, p in enumerate(paras):
            if p["role"] == "title":
                text = p["text"].strip()
                if text.upper() in {"TITLE", "TITLE:"}:
                    for j in range(i + 1, min(i + 5, len(paras))):
                        nxt = paras[j]
                        if nxt["role"] in {"body", "title"} and len(nxt["text"].strip()) > 5:
                            return nxt["text"].strip()
                return text
        return paras[1]["text"].strip() if len(paras) > 1 else ""

    # ── Authors + Affiliations ─────────────────────────────────────────────────

    # Compiled once at class scope for speed. Detects Unicode superscript
    # digits (¹²³⁴⁵⁶⁷⁸⁹⁰) and the common footnote symbols (†‡§).
    _SUPERSCRIPT_RE = re.compile(
        r"[\u00b9\u00b2\u00b3\u2074-\u2079\u2070\u2071\u207f"
        r"\u2020\u2021\u00a7*]"
    )

    # Affiliation-signal words tested with word-boundary matching.
    _AFF_WORD_SET = {
        "university", "institute", "department", "dept", "college",
        "laboratory", "lab", "centre", "center", "school", "faculty",
        "iit", "nit", "iisc", "hospital", "corporation", "corp", "ltd",
        # country / city names that appear almost exclusively in affiliations
        "india", "usa", "uk", "china", "germany", "france", "japan",
        "canada", "australia", "brazil", "korea", "singapore",
        # job-title signals
        "professor", "researcher", "engineer", "scientist", "lecturer",
        "email",
    }
    # Substring signals (can't use word-boundary for these)
    _AFF_SUBSTR_SET = {"@", ".edu", ".ac.", ".org", ".gov", ".in"}

    def _line_is_affiliation(self, text: str, role: str) -> bool:
        """
        Returns True when a paragraph line is an affiliation rather than an
        author name. Checked in priority order:

          1. Classifier already labelled it "affiliation"
          2. Starts with a superscript digit/symbol  (¹Department…)
          3. Contains an email address               (foo@bar.edu)
          4. Contains a known affiliation word       (university, dept, …)
          5. Contains a known affiliation substring  (.edu, .ac., …)
          6. Very long line unlikely to be just names (>10 words without comma)

        Deliberately does NOT fire on lines that are just person names, even
        names with trailing superscripts (Rahul Sharma¹ → author, not aff).
        """
        if role == "affiliation":
            return True

        # Superscript at the START of the line → affiliation number prefix
        if text and self._SUPERSCRIPT_RE.match(text[0]):
            return True

        text_lower = text.lower()

        # Email anywhere on the line
        if "@" in text:
            return True

        # Word-boundary check against known affiliation words
        words = re.findall(r"\b\w+\b", text_lower)
        if any(w in self._AFF_WORD_SET for w in words):
            return True

        # Substring check (handles .edu, .ac.uk etc.)
        if any(s in text_lower for s in self._AFF_SUBSTR_SET):
            return True

        return False

    def _clean_author_name(self, raw: str) -> str | None:
        """
        Strips trailing/embedded superscript markers from an author name and
        returns a cleaned name string, or None if the result looks invalid.

        Works for any name, including:
          • ASCII:      "Rahul Sharma¹"        → "Rahul Sharma"
          • Initials:   "John A. Smith²"       → "John A. Smith"
          • Hyphenated: "Marie-Curie Dupont³"  → "Marie-Curie Dupont"
          • Non-ASCII:  "André Müller¹"        → "André Müller"
          • Multi:      "Jane Doe¹, Bob Lee²"  (split separately before call)
        """
        # Strip superscripts from anywhere in the string
        name = self._SUPERSCRIPT_RE.sub("", raw).strip(" ,;")

        # Collapse internal whitespace
        name = re.sub(r"\s+", " ", name).strip()

        if not name:
            return None

        # Reject if it looks like an affiliation that slipped through
        if self._line_is_affiliation(name, "author"):
            return None

        # Reject pure label tokens
        if name.upper() in {"AUTHORS", "AUTHOR", "TITLE", ""}:
            return None

        # Reject single-character "names" (stray initials after strip)
        if len(name) <= 1:
            return None

        return name

    def _split_multi_author_line(self, text: str) -> list[str]:
        """
        Splits a single line that may contain several author names separated
        by commas or 'and', e.g.:

          "Jane Doe¹, Bob Lee², Carol Ann Smith³"
          "Alice Brown and Dave White"

        Returns a list of raw name strings (still carrying superscripts).
        """
        # Split on comma or ' and ' (word boundary)
        parts = re.split(r",\s*|\s+and\s+", text, flags=re.IGNORECASE)
        return [p.strip() for p in parts if p.strip()]

    def _extract_authors_and_affiliations(
        self, paras: list
    ) -> tuple[list[str], list[str]]:
        """
        Improved linking of authors and affiliations using positional proximity
        and superscript matching.
        """
        _STOP_ROLES = {
            "abstract", "abstract_heading",
            "keywords", "keywords_heading",
            "section_heading", "sub_heading",
            "reference", "figure_caption", "table_caption",
        }
        _STOP_TEXT_UPPER = _STRUCTURAL_HEADINGS | _CAPS_SECTION_LABELS

        # 1. Collect the header zone paragraphs
        zone: list[dict] = []
        in_zone = False

        for p in paras:
            role  = p["role"]
            text  = p["text"].strip()
            upper = text.upper().strip()

            if not in_zone:
                if role in {"title", "author", "affiliation"} or upper in {"AUTHORS", "AUTHOR"}:
                    in_zone = True
                    if upper in {"AUTHORS", "AUTHOR", "TITLE"} or role == "title":
                        continue
                else:
                    continue

            if role in _STOP_ROLES or upper in _STOP_TEXT_UPPER:
                break

            zone.append(p)

        # 2. Extract and Pair using positional proximity
        raw_authors: list[str] = []
        groupings: dict[int, list[str]] = {} # index -> list of lines
        
        current_author_indices: list[int] = []
        seen_authors = set()
        
        sup_chars = ["¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"]
        _TRAIL_SUP = re.compile(r"([\u00b9\u00b2\u00b3\u2074-\u2079\u2070\u2071\u207f\u2020\u2021\u00a7*]+)$")
        _LEAD_SUP  = re.compile(r"^([\u00b9\u00b2\u00b3\u2074-\u2079\u2070\u2071\u207f\u2020\u2021\u00a7*]+)")

        for p in zone:
            role = p["role"]
            text = p["text"].strip()
            if not text: continue

            if self._line_is_affiliation(text, role):
                # AFFILIATION LINE
                m_lead = _LEAD_SUP.match(text)
                if m_lead:
                    sup = m_lead.group(1)
                    matched_indices = []
                    for idx, a_name in enumerate(raw_authors):
                        m_trail = _TRAIL_SUP.search(a_name)
                        if m_trail and m_trail.group(1) == sup:
                            matched_indices.append(idx)
                    
                    if matched_indices:
                        for idx in matched_indices:
                            groupings.setdefault(idx, []).append(text)
                        continue
                
                # Proximity fallback
                if current_author_indices:
                    for idx in current_author_indices:
                        groupings.setdefault(idx, []).append(text)
            else:
                # AUTHOR LINE
                parts = self._split_multi_author_line(text)
                new_indices = []
                for raw_name in parts:
                    clean = self._clean_author_name(raw_name)
                    if clean and clean not in seen_authors:
                        m_sup = _TRAIL_SUP.search(raw_name)
                        name_with_sup = clean + (m_sup.group(1) if m_sup else "")
                        
                        raw_authors.append(name_with_sup)
                        seen_authors.add(clean)
                        new_indices.append(len(raw_authors) - 1)
                
                if new_indices:
                    current_author_indices = new_indices

        # 3. Final Formatting
        final_authors = []
        final_affiliations = []
        
        for i, name_ws in enumerate(raw_authors):
            clean_name = self._clean_author_name(name_ws)
            sup = sup_chars[i % len(sup_chars)]
            final_authors.append(f"{clean_name}{sup}")
            
            lines = groupings.get(i, [])
            if lines:
                cleaned_lines = []
                for l in lines:
                    cleaned_lines.append(_LEAD_SUP.sub("", l).strip())
                combined = ", ".join(cleaned_lines)
                final_affiliations.append(f"{sup} {combined}")

        return final_authors, final_affiliations


    def _split_name_affiliation(self, text: str) -> tuple[str | None, str | None]:
        """
        Improved splitting — more flexible and handles common real-world cases
        """
        if not text:
            return None, None

        lower = text.lower()

        # Quick exits
        if "@" in text and len(text.split()) <= 3:
            return None, text.strip()  # probably just email

        # Common title prefixes
        title_prefixes = r"(?i)^(dr\.?|prof\.?|mr\.?|ms\.?|mrs\.?|miss)?\s*"

        # Try to find the first strong affiliation marker
        aff_markers = [
            "department", "dept", "school", "institute", "university", "center", "lab",
            "college", "faculty", "address", "email", "@", ".edu", ".ac.", ".in", "india"
        ]

        words = text.split()
        name_parts = []
        aff_start_idx = len(words)

        for i, word in enumerate(words):
            clean_word = re.sub(r"[^a-zA-Z]", "", word).lower()
            if any(marker in clean_word for marker in aff_markers) or "@" in word:
                aff_start_idx = i
                break
            # also stop if we see comma followed by title-like word
            if word.endswith(",") and i + 1 < len(words):
                next_w = words[i+1].lower()
                if next_w in {"assistant", "associate", "professor", "dr", "mr", "ms"}:
                    aff_start_idx = i + 1
                    break

        if aff_start_idx == 0:
            # whole line looks like affiliation
            return None, text.strip()

        if aff_start_idx == len(words):
            # no affiliation marker → probably just name
            name = text.strip()
            # but if very long → suspicious
            if len(words) > 8:
                return None, None
            return name, None

        name = " ".join(words[:aff_start_idx]).strip().rstrip(",")
        aff = " ".join(words[aff_start_idx:]).strip()

        # Post-clean name
        name = re.sub(r"\s+", " ", name).strip()
        if re.match(r"^[A-Z]\.?$", name) or len(name.split()) == 1:
            # too short → probably not a real name
            return None, text.strip()

        return name, aff
    # ── Abstract ───────────────────────────────────────────────────────────────

    def _extract_abstract(self, paras: list) -> str:
        in_abstract = False
        parts: list = []

        for p in paras:
            role  = p["role"]
            text  = p["text"].strip()
            upper = text.upper().strip()

            if role == "abstract":
                return re.sub(
                    r"^(abstract\s*[—\-:]\s*|ABSTRACT\s+)", "", text, flags=re.I
                ).strip() or text

            if role == "abstract_heading" or upper == "ABSTRACT":
                in_abstract = True
                continue

            if in_abstract:
                if role == "body" and len(text) > 30:
                    parts.append(text)
                elif role in {"keywords", "keywords_heading", "section_heading"} \
                        or upper in {"KEYWORDS", "KEYWORD", "INDEX TERMS"}:
                    break

        if parts:
            return " ".join(parts)

        # Fallback: first body paragraph > 150 chars
        for p in paras:
            if p["role"] == "body" and len(p["text"]) > 150:
                return p["text"].strip()
        return ""

    # ── Keywords (BUG-3) ───────────────────────────────────────────────────────

    def _extract_keywords(self, paras: list) -> str:
        """
        Walk forward from keywords_heading / keywords role node only.
        Old code searched the whole document for 'Large Language Models' in text
        → matched the title paragraph first → returned title text as keywords.
        """
        in_kw = False

        for p in paras:
            role  = p["role"]
            text  = p["text"].strip()
            upper = text.upper().strip()

            if role == "keywords":
                return re.sub(
                    r"^(keywords?|index terms?)\s*[—\-:]\s*", "", text, flags=re.I
                ).strip() or text

            if role == "keywords_heading" or upper in {
                "KEYWORDS", "KEYWORD", "INDEX TERMS"
            }:
                in_kw = True
                continue

            if in_kw:
                if role == "body":
                    return text      # first body para after heading = keywords
                elif role != "body":
                    break            # any non-body = end of keywords block

        return re.sub(r"(?i)^(index\s+terms?|keywords?)\s*[-—:]*\s*", "", text).strip()

    # ── Sections ──────────────────────────────────────────────────────────────

    # Matches Roman-numeral section headings produced by the parser:
    # "I. INTRODUCTION"  "II. RELATED WORK"  "XIV. CONCLUSION"
    _ROMAN_HDR_RE = re.compile(
        r"^(XIV|XIII|XII|XI|X{1,3}|IX|VIII|VII|VI|IV|V|V?I{1,3}|II|I)\."
        r"(\s+[A-Z][A-Z0-9\s\-]{0,60})?$",
        re.IGNORECASE,
    )
    # Numeric sub-heading: "3.1 Title", "4.2.1 Detail"
    _NUMERIC_SUB_RE = re.compile(r"^\d+\.\d+(\.\d+)?\s+\S")
    # Alpha sub-heading: "A. Feature Extraction"  (single uppercase letter + dot)
    _ALPHA_SUB_RE   = re.compile(r"^[A-Z]\.\s+\S")

    # Roles that should NEVER be collected as section body content
    _SECTION_SKIP_ROLES = {
        "title", "author", "affiliation",
        "abstract", "abstract_heading",
        "keywords", "keywords_heading",
        "reference",
    }

    def _is_section_heading(self, text: str, role: str) -> bool:
        """
        Returns True if this paragraph is a major section heading.

        Accepts:
          • role == "section_heading"   (classifier/parser promoted it)
          • Roman numeral prefix        ("I. INTRODUCTION")
          • Standalone known-heading text ("INTRODUCTION", "CONCLUSION", …)
        """
        if role == "section_heading":
            return True
        if self._ROMAN_HDR_RE.match(text.strip()):
            return True
        if text.strip().upper() in _KNOWN_HEADINGS_UPPER:
            return True
        return False

    def _is_sub_heading(self, text: str, role: str) -> bool:
        """
        Returns True if this paragraph is a sub-section heading.

        Accepts:
          • role == "sub_heading"         (classifier/parser promoted it)
          • Numeric prefix  "3.1 Title"
          • Alpha prefix    "A. Title"
        """
        if role == "sub_heading":
            return True
        if self._NUMERIC_SUB_RE.match(text.strip()) and len(text.split()) <= 12:
            return True
        if self._ALPHA_SUB_RE.match(text.strip()) and len(text.split()) <= 8:
            return True
        return False

    def _extract_sections(self, paras: list) -> list[dict]:
        """
        Builds the sections list from classifier-labelled paragraphs.

        Structure returned:
          [
            {
              "heading": "I. INTRODUCTION",
              "content": [
                {"text": "...", "role": "body"},
                {
                  "subheading": "A. Background",
                  "content": [{"text": "...", "role": "body"}, ...]
                },
                ...
              ]
            },
            ...
          ]

        ── Key design decisions ──────────────────────────────────────────
        1. _SECTION_SKIP_ROLES: title/author/affiliation/abstract/keywords/
           reference paragraphs are explicitly skipped — they cannot be
           body content of any section regardless of document position.

        2. _STRUCTURAL_HEADINGS filter: REFERENCES, ACKNOWLEDGMENTS, etc.
           trigger in_references / in_ack states in their own extractors.
           They are NOT added as numbered body sections.

        3. Fused body paragraphs: if a body paragraph starts with an
           ALL-CAPS label that matches _CAPS_SECTION_LABELS (e.g. the
           parser failed to split "RELATED WORK Early attempts…") we
           promote the label to a section heading and the remainder to
           the first body paragraph of that section.

        4. Sub-headings without a prior section: they are promoted into
           a new anonymous section so content is never lost.

        5. After-abstract boundary: sections only start collecting after
           we have passed the abstract/keywords zone. This prevents
           abstract body text from being misidentified as a section.
        """
        sections: list[dict]       = []
        current_section: dict | None = None
        current_sub: dict | None     = None
        past_header_zone             = False  # True once we pass abstract/keywords

        def _flush_sub():
            """Append current sub-section into current section's content."""
            nonlocal current_sub
            if current_sub is not None and current_section is not None:
                current_section["content"].append(current_sub)
            current_sub = None

        def _flush_section():
            """Append current section into the sections list."""
            nonlocal current_section
            _flush_sub()
            if current_section is not None:
                sections.append(current_section)
            current_section = None

        for p in paras:
            role  = p["role"]
            text  = p["text"].strip()
            upper = text.upper().strip()

            # ── Structural roles that mark end of section content ─────────
            if role in {"abstract", "abstract_heading",
                        "keywords", "keywords_heading"}:
                past_header_zone = False  # still in header
                continue

            # Mark that we have cleared the header zone
            if role in {"section_heading", "sub_heading"} or (
                role == "body" and upper in _CAPS_SECTION_LABELS
            ):
                past_header_zone = True

            # ── Roles to skip entirely ────────────────────────────────────
            if role in self._SECTION_SKIP_ROLES or p.get("is_table_component"):
                continue

            # ── Structural headings (REFERENCES / ACKNOWLEDGMENT) ─────────
            if upper in _STRUCTURAL_HEADINGS:
                _flush_section()
                past_header_zone = True
                continue

            # ── Major section heading ─────────────────────────────────────
            if self._is_section_heading(text, role):
                if upper in _STRUCTURAL_HEADINGS:
                    _flush_section()
                    continue
                _flush_section()
                past_header_zone = True
                current_section = {"heading": text, "content": []}
                # DEBUG: print(f"[mapper] NEW SECTION: {text!r}")
                continue

            # ── Fused body paragraph starting with an ALL-CAPS section label
            # e.g. "RELATED WORK Early attempts on multi-agent systems..."
            if role == "body" and not past_header_zone is False:
                m = _CAPS_PREFIX_RE.match(text)
                if m:
                    label = m.group(1).strip()
                    if label in _CAPS_SECTION_LABELS:
                        _flush_section()
                        past_header_zone = True
                        remainder = text[m.end():].strip()
                        current_section = {"heading": label, "content": []}
                        # DEBUG: print(f"[mapper] FUSED SECTION: {label!r} | body: {remainder[:50]!r}")
                        if remainder:
                            current_section["content"].append(
                                {"text": remainder, "role": "body"}
                            )
                        continue

            # ── Sub-heading ───────────────────────────────────────────────
            if self._is_sub_heading(text, role):
                if current_section is None:
                    # Promote to anonymous section so nothing is lost
                    _flush_section()
                    current_section = {"heading": "", "content": []}
                _flush_sub()
                current_sub = {"subheading": text, "content": []}
                # DEBUG: print(f"[mapper] SUB-HEADING: {text!r}")
                continue

            # ── Body / caption content ────────────────────────────────────
            if not text:
                continue  # blank line

            if current_section is None:
                # Body text before any section heading — skip silently
                continue

            entry = {"text": text, "role": role}

            if current_sub is not None:
                current_sub["content"].append(entry)
            else:
                current_section["content"].append(entry)

        # Flush anything remaining
        _flush_section()

        if len(sections) < 2:
            import logging
            logging.getLogger(__name__).warning("Very few headings detected — possible detection failure")
            print("[mapper] WARNING: Very few headings detected — possible detection failure")

        # DEBUG: print(f"[mapper] sections extracted: {[s['heading'] for s in sections]}")
        return sections

    def _extract_tables_from_text(self, items: list) -> list[dict]:
        """
        Recursively scans content items for paragraphs that look like tables.
        Uses the same robust splitting as parser.py.
        """
        extracted_tables = []
        i = 0
        while i < len(items):
            item = items[i]
            
            # 1. Recurse into nested content
            if "content" in item and isinstance(item["content"], list):
                nested_tables = self._extract_tables_from_text(item["content"])
                extracted_tables.extend(nested_tables)

            # 2. Check current paragraph for table caption
            if "text" in item and re.match(r"^TABLE\s+[IVX\d]+", item["text"].strip(), re.I):
                caption = item["text"].strip()
                table_rows = []
                
                j = i + 1
                while j < len(items):
                    next_item = items[j]
                    if "text" in next_item:
                        txt = next_item["text"].strip()
                        # Use robust splitting logic directly here (re-implementation of parser logic)
                        parts = [p.strip() for p in re.split(r"\t|\s{3,}", txt) if p.strip()]
                        if len(parts) < 2:
                            parts = [p.strip() for p in re.split(r"\t|\s{2,}", txt) if p.strip()]
                        
                        if len(parts) >= 2:
                            # Basic unit-merge logic for consistency
                            refined = []
                            for p in parts:
                                if refined and (p.startswith("(") or p.lower() in {"%", "(%)", "(ms)", "(kb)", "(mb)", "(ours)"}):
                                    refined[-1] = f"{refined[-1]} {p}"
                                else:
                                    refined.append(p)
                            table_rows.append(refined)
                            j += 1
                        else:
                            break
                    else:
                        break
                
                if table_rows:
                    extracted_tables.append({
                        "caption": caption,
                        "rows": table_rows # Use 'rows' for consistency with parser
                    })
                    del items[i:j]
                    continue 
            i += 1
        return extracted_tables

    # ── References ─────────────────────────────────────────────────────────────

    def _extract_references(self, paras: list) -> list:
        refs: list = []
        in_ref = False
        seen: set = set()

        _BRACKET = re.compile(r"^\[\d+\]")
        _NUMERIC  = re.compile(r"^\d+\.\s")
        _AUTHOR   = re.compile(r"^[A-Z][A-Za-z\-]+,?\s.{0,60}\(\d{4}\)")

        for p in paras:
            role  = p["role"]
            text  = p["text"].strip()
            upper = text.upper().strip()

            if role == "reference":
                if text not in seen:
                    refs.append(text)
                    seen.add(text)
                continue

            if role == "section_heading" and upper in {"REFERENCES", "BIBLIOGRAPHY"}:
                in_ref = True
                continue

            if role == "section_heading" and upper not in {"REFERENCES", "BIBLIOGRAPHY"}:
                in_ref = False

            if in_ref and role == "body":
                if _BRACKET.match(text) or _NUMERIC.match(text) or _AUTHOR.match(text):
                    if text not in seen:
                        refs.append(text)
                        seen.add(text)

        return refs

    # ── Acknowledgments (BUG-4) ───────────────────────────────────────────────

    def _extract_acknowledgments(self, paras: list) -> str:
        """
        Old code: 'if acknowledg in text.lower(): return text'
        → matched para[51] role=section_heading text='ACKNOWLEDGMENTS' first
        → returned the heading label as ack text.

        Fix: enter a collection state on the heading; return the BODY paragraph(s)
        that follow it.
        """
        parts: list = []
        in_ack = False
        ACK = {"ACKNOWLEDGMENT", "ACKNOWLEDGMENTS", "ACKNOWLEDGEMENTS"}

        for p in paras:
            role  = p["role"]
            text  = p["text"].strip()
            upper = text.upper().strip()

            if role == "section_heading" and upper in ACK:
                in_ack = True
                continue

            # Handle inline CAPS label format (rare edge case)
            if upper in ACK and role != "section_heading":
                in_ack = True
                rest = text[len(upper):].strip(" —:-")
                if rest:
                    parts.append(rest)
                continue

            if in_ack:
                if role == "body":
                    parts.append(text)
                elif role in {"section_heading", "reference"}:
                    break

        return " ".join(parts)

    # ── Paragraph validation (stub) ────────────────────────────────────────────

    def _validate_paragraph(self, para: dict) -> dict:
        return {"is_valid": True, "violations": {}, "spec_properties": {}}


# ── Local test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    input_json  = r"D:\DATA SCIENCE AND ML\Project\ManuscriptMagic.AI\template\test.json"
    ieee_spec   = r"D:\DATA SCIENCE AND ML\Project\ManuscriptMagic.AI\backend\templates\ieee.json"
    output_json = "debug_mapped_fixed.json"

    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    m = ContentMapper(ieee_spec)
    result = m.map_content(data)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"title:        {result['title']}")
    print(f"authors:      {result['authors']}")
    print(f"affiliations: {[a[:60] for a in result['affiliations']]}")
    print(f"abstract:     {result['abstract'][:100]}...")
    print(f"keywords:     {result['keywords']}")
    print(f"sections:     {[s['heading'] for s in result['sections']]}")
    print(f"references:   {len(result['references'])}")
    print(f"ack:          {result['acknowledgments'][:80]}")