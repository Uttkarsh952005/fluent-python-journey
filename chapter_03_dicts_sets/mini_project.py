"""
Chapter 3: Mini Project — Text Analysis Engine
===============================================
A word frequency and co-occurrence analysis engine using dicts and sets.

Features:
  - Word frequency counter (Counter with real interpretation)
  - Inverted index: word → set of documents it appears in
  - Document similarity using set algebra (Jaccard index)
  - Vocabulary comparison across multiple texts
  - Top-N words with context (which documents, not just count)

This is NOT a tutorial demo — it's a tool you could actually use to
compare writing styles, detect duplicate content, or index documents.

Concepts demonstrated from Chapter 3:
  - Counter for frequency + arithmetic
  - defaultdict(set) for inverted index
  - frozenset for stable, hashable document representations
  - set operations (intersection, union, difference) for comparison
  - dict.keys() views for vocabulary algebra
  - MappingProxyType for read-only exposure of internal state

Run with: python mini_project.py
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from types import MappingProxyType
from typing import Iterator

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Text Preprocessing
# ─────────────────────────────────────────────────────────────────────────────

# Words to ignore — closed-class vocabulary with no semantic content
STOPWORDS: frozenset[str] = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "it", "its", "this", "that", "these", "those",
    "by", "from", "as", "so", "if", "not", "no", "than", "then", "there",
    "their", "they", "we", "you", "i", "he", "she", "his", "her", "our",
    "all", "also", "more", "other", "into", "which", "when", "who", "can",
})


def tokenize(text: str) -> list[str]:
    """
    Extract lowercase alphabetic words from text, filtering stopwords.
    Returns tokens as a list — order preserved for frequency counting.
    """
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


# ─────────────────────────────────────────────────────────────────────────────
# Core Engine
# ─────────────────────────────────────────────────────────────────────────────


class TextCorpus:
    """
    A collection of named text documents with word-level analysis.

    Internally maintains:
    - _doc_tokens:   dict[str, list[str]]           name → token list
    - _frequencies:  dict[str, Counter[str]]         name → word counts
    - _inverted:     defaultdict[str, set[str]]      word → {doc names}
    - _vocabulary:   dict[str, int]                  word → total occurrences

    The public API exposes these via read-only MappingProxyType views
    where mutation would break internal consistency.
    """

    def __init__(self) -> None:
        self._doc_tokens:  dict[str, list[str]]      = {}
        self._frequencies: dict[str, Counter[str]]   = {}
        self._inverted:    defaultdict[str, set[str]] = defaultdict(set)
        self._vocabulary:  Counter[str]               = Counter()

    def add_document(self, name: str, text: str) -> None:
        """
        Add a document to the corpus. Rebuilds all indices.
        """
        if name in self._doc_tokens:
            raise ValueError(f"Document '{name}' already in corpus. Use a unique name.")

        tokens = tokenize(text)
        if not tokens:
            raise ValueError(f"Document '{name}' produced no tokens after filtering.")

        self._doc_tokens[name] = tokens
        self._frequencies[name] = Counter(tokens)

        # Inverted index: word → which documents contain it
        # Using defaultdict(set) — each word maps to a set of document names
        for word in set(tokens):   # set() de-dupes: one entry per doc per word
            self._inverted[word].add(name)

        # Global vocabulary: total word counts across all documents
        self._vocabulary.update(tokens)

    # ──────────────────────────────────────────────────────────────────────
    # Frequency Analysis
    # ──────────────────────────────────────────────────────────────────────

    def top_words(self, n: int = 10, doc: str | None = None) -> list[tuple[str, int]]:
        """
        Return top-N words by frequency.
        If doc is given, rank within that document; otherwise across all documents.
        """
        if doc is not None:
            if doc not in self._frequencies:
                raise KeyError(f"No document named '{doc}'")
            return self._frequencies[doc].most_common(n)
        return self._vocabulary.most_common(n)

    def word_frequency(self, word: str, doc: str | None = None) -> int:
        """Frequency of a word in a specific document or across the corpus."""
        w = word.lower()
        if doc is not None:
            return self._frequencies.get(doc, Counter()).get(w, 0)
        return self._vocabulary.get(w, 0)

    def documents_containing(self, word: str) -> frozenset[str]:
        """
        Return the set of documents that contain a word.
        Returns frozenset — immutable, hashable, safe to use as dict key.
        """
        return frozenset(self._inverted.get(word.lower(), set()))

    # ──────────────────────────────────────────────────────────────────────
    # Set Algebra: Vocabulary and Similarity
    # ──────────────────────────────────────────────────────────────────────

    def vocabulary(self, doc: str | None = None) -> frozenset[str]:
        """
        Vocabulary of a document (or entire corpus).
        frozenset: unique words, hashable, supports set operations.
        """
        if doc is not None:
            return frozenset(self._frequencies.get(doc, {}).keys())
        return frozenset(self._vocabulary.keys())

    def jaccard_similarity(self, doc_a: str, doc_b: str) -> float:
        """
        Jaccard index: |A ∩ B| / |A ∪ B|.
        Measures vocabulary overlap between two documents.
        0.0 = no common words, 1.0 = identical vocabulary.

        Uses frozenset intersection and union — clean set algebra.
        """
        vocab_a = self.vocabulary(doc_a)
        vocab_b = self.vocabulary(doc_b)
        if not vocab_a and not vocab_b:
            return 1.0  # two empty docs are identical
        intersection = vocab_a & vocab_b
        union = vocab_a | vocab_b
        return len(intersection) / len(union)

    def shared_vocabulary(self, *doc_names: str) -> frozenset[str]:
        """Words that appear in ALL named documents (intersection)."""
        if not doc_names:
            return frozenset()
        vocabs = [self.vocabulary(d) for d in doc_names]
        return vocabs[0].intersection(*vocabs[1:])

    def exclusive_vocabulary(self, doc: str, *others: str) -> frozenset[str]:
        """Words in `doc` that appear in NO other named document."""
        doc_vocab = self.vocabulary(doc)
        others_vocab = frozenset().union(*(self.vocabulary(d) for d in others))
        return doc_vocab - others_vocab

    # ──────────────────────────────────────────────────────────────────────
    # Cross-Document Analysis
    # ──────────────────────────────────────────────────────────────────────

    def common_rare_words(
        self, min_docs: int = 2, max_corpus_freq: int = 5
    ) -> list[tuple[str, int]]:
        """
        Words that appear in at least `min_docs` documents
        but have low overall corpus frequency (potentially meaningful terms).

        These are good candidates for topic-specific vocabulary.
        """
        results = []
        for word, doc_set in self._inverted.items():
            if len(doc_set) >= min_docs:
                total = self._vocabulary[word]
                if total <= max_corpus_freq:
                    results.append((word, total))
        return sorted(results, key=lambda x: x[1])

    def similarity_matrix(self) -> dict[tuple[str, str], float]:
        """
        Compute pairwise Jaccard similarity for all document pairs.
        Returns a dict with (doc_a, doc_b) tuples as keys.
        Only upper triangle (no repeats, no self-comparison).
        """
        docs = list(self._doc_tokens.keys())
        matrix: dict[tuple[str, str], float] = {}
        for i, a in enumerate(docs):
            for b in docs[i + 1:]:
                matrix[(a, b)] = self.jaccard_similarity(a, b)
        return matrix

    # ──────────────────────────────────────────────────────────────────────
    # Read-Only Views (MappingProxyType)
    # ──────────────────────────────────────────────────────────────────────

    @property
    def frequencies(self) -> MappingProxyType[str, Counter[str]]:
        """Read-only view of per-document frequency counters."""
        return MappingProxyType(self._frequencies)

    @property
    def inverted_index(self) -> MappingProxyType[str, set[str]]:
        """Read-only view of the inverted index."""
        return MappingProxyType(dict(self._inverted))

    # ──────────────────────────────────────────────────────────────────────
    # Reporting
    # ──────────────────────────────────────────────────────────────────────

    def report(self) -> None:
        """Print a summary report across all documents."""
        print(f"\nCorpus: {len(self._doc_tokens)} documents, "
              f"{len(self._vocabulary):,} unique words, "
              f"{sum(self._vocabulary.values()):,} total tokens\n")

        for doc_name in self._doc_tokens:
            freq = self._frequencies[doc_name]
            tokens = self._doc_tokens[doc_name]
            print(f"  [{doc_name}]  {len(tokens)} tokens, "
                  f"{len(freq)} unique words")
            top5 = freq.most_common(5)
            print(f"    Top 5: {', '.join(f'{w}({c})' for w, c in top5)}")


# ─────────────────────────────────────────────────────────────────────────────
# Sample Data
# ─────────────────────────────────────────────────────────────────────────────

PYTHON_ZEN = """
Beautiful is better than ugly. Explicit is better than implicit.
Simple is better than complex. Complex is better than complicated.
Flat is better than nested. Sparse is better than dense.
Readability counts. Special cases aren't special enough to break the rules.
Although practicality beats purity. Errors should never pass silently.
Unless explicitly silenced. In the face of ambiguity, refuse the temptation to guess.
There should be one and preferably only one obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never. Although never is often better than right now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea. Let's do more of those!
"""

UNIX_PHILOSOPHY = """
Write programs that do one thing and do it well. Write programs to work together.
Write programs to handle text streams, because that is a universal interface.
The rule of modularity: build simple parts connected by clean interfaces.
The rule of clarity: clarity is better than cleverness.
The rule of composition: design programs to be connected to other programs.
The rule of separation: separate policy from mechanism.
The rule of simplicity: design for simplicity.
The rule of parsimony: write a big program only when nothing else will do.
The rule of transparency: design for visibility to make inspection possible.
The rule of robustness: robustness is the child of transparency and simplicity.
"""

AGILE_MANIFESTO = """
Individuals and interactions over processes and tools.
Working software over comprehensive documentation.
Customer collaboration over contract negotiation.
Responding to change over following a plan.
We value simplicity: the art of maximizing the amount of work not done.
Continuous attention to technical excellence and good design enhances agility.
Build projects around motivated individuals. Give them the environment and support.
The most efficient method of conveying information within a team is face to face.
Simplicity is essential. The best architectures emerge from self-organizing teams.
"""


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    print("=" * 60)
    print("  Text Analysis Engine — Chapter 3 Mini Project")
    print("=" * 60)

    corpus = TextCorpus()
    corpus.add_document("zen_of_python", PYTHON_ZEN)
    corpus.add_document("unix_philosophy", UNIX_PHILOSOPHY)
    corpus.add_document("agile_manifesto", AGILE_MANIFESTO)

    corpus.report()

    # ── Similarity matrix ────────────────────────────────────────────────
    print("\n── Pairwise Jaccard Similarity ──")
    matrix = corpus.similarity_matrix()
    for (a, b), score in sorted(matrix.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(score * 20)
        print(f"  {a:<20} ↔ {b:<20}  {score:.3f}  {bar}")

    print("""
  Jaccard similarity = |shared vocab| / |combined vocab|
  Higher score → more vocabulary overlap → more similar content
""")

    # ── Shared vocabulary (in all three) ─────────────────────────────────
    shared = corpus.shared_vocabulary("zen_of_python", "unix_philosophy", "agile_manifesto")
    print(f"── Words in ALL 3 documents ──")
    print(f"  {sorted(shared)}\n")

    # ── Exclusive vocabulary (set difference) ────────────────────────────
    zen_only = corpus.exclusive_vocabulary(
        "zen_of_python", "unix_philosophy", "agile_manifesto"
    )
    print(f"── Words ONLY in 'zen_of_python' ──")
    print(f"  {sorted(zen_only)[:15]}...\n")

    unix_only = corpus.exclusive_vocabulary(
        "unix_philosophy", "zen_of_python", "agile_manifesto"
    )
    print(f"── Words ONLY in 'unix_philosophy' ──")
    print(f"  {sorted(unix_only)[:15]}...\n")

    # ── Inverted index lookup ─────────────────────────────────────────────
    print("── Inverted Index: which docs contain 'simplicity'? ──")
    docs = corpus.documents_containing("simplicity")
    print(f"  'simplicity' appears in: {sorted(docs)}")
    print(f"  (type: {type(docs).__name__} — hashable, usable as dict key)\n")

    # ── Using frozenset as a dict key ─────────────────────────────────────
    doc_group: dict[frozenset[str], str] = {
        corpus.documents_containing("simplicity"): "simplicity cluster",
        corpus.documents_containing("better"): "better/comparison cluster",
    }
    print("── frozenset as dict keys (document clusters) ──")
    for doc_set, label in doc_group.items():
        print(f"  {label}: {sorted(doc_set)}")

    # ── Top words comparison ──────────────────────────────────────────────
    print("\n── Top 8 words per document ──")
    for doc_name in ["zen_of_python", "unix_philosophy", "agile_manifesto"]:
        top = corpus.top_words(8, doc=doc_name)
        print(f"  [{doc_name}]")
        print(f"    {', '.join(f'{w}({c})' for w, c in top)}")

    # ── Read-only proxy demonstration ─────────────────────────────────────
    print("\n── MappingProxyType: read-only inverted index ──")
    proxy = corpus.inverted_index
    print(f"  type: {type(proxy).__name__}")
    print(f"  proxy['simplicity']: {sorted(proxy['simplicity'])}")
    try:
        proxy["new_word"] = {"fake_doc"}  # type: ignore[index]
    except TypeError as e:
        print(f"  Mutation attempt → {e}")

    # ── Counter arithmetic ────────────────────────────────────────────────
    print("\n── Counter arithmetic: zen + unix word pools ──")
    zen_freq = corpus.frequencies["zen_of_python"]
    unix_freq = corpus.frequencies["unix_philosophy"]

    combined = zen_freq + unix_freq
    shared_words = zen_freq & unix_freq   # min count per word
    print(f"  Combined top 5: {combined.most_common(5)}")
    print(f"  Words in BOTH (min count): {sorted(dict(shared_words).items())[:5]}")


if __name__ == "__main__":
    main()
