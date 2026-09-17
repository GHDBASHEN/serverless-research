"""
================================================================================
MACRO-BENCHMARK: Text Analytics & NLP Document Processing
================================================================================
Simulates serverless document parsing and text processing:
  - Text normalization, sanitization, and tokenization
  - Stopword filtering and vocabulary frequency counting
  - Lexicon-based sentiment scoring calculation
================================================================================
"""

import re
import random
import time
from collections import Counter


STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "as", "at", "be", "because", "been", "before", "being", "below",
    "between", "both", "but", "by", "could", "did", "do", "does", "doing", "down",
    "during", "each", "few", "for", "from", "further", "had", "has", "have", "having",
    "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i",
    "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more", "most",
    "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only",
    "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she",
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "through", "to",
    "too", "under", "until", "up", "very", "was", "we", "were", "what", "when", "where",
    "which", "while", "who", "whom", "why", "with", "would", "you", "your", "yours"
}

POSITIVE_WORDS = {"good", "great", "excellent", "fast", "reliable", "scalable", "optimized", "high"}
NEGATIVE_WORDS = {"slow", "bad", "expensive", "failure", "timeout", "latency", "error", "bottleneck"}


def text_document_analysis(num_documents: int = 1500) -> dict:
    """
    Simulates ingesting and analyzing customer reviews or log documents.
    """
    words_pool = [
        "serverless", "cloud", "latency", "fast", "aws", "azure", "gcp",
        "lambda", "timeout", "reliable", "database", "query", "cost",
        "expensive", "scalable", "optimized", "performance", "error"
    ]

    total_tokens = 0
    sentiment_scores = []
    overall_vocab = Counter()

    for i in range(num_documents):
        # Build synthetic review document
        doc_len = random.randint(15, 35)
        raw_text = " ".join(random.choices(words_pool, k=doc_len))

        # 1. Clean and tokenize
        tokens = re.findall(r"\b[a-z]+\b", raw_text.lower())
        total_tokens += len(tokens)

        # 2. Filter stopwords
        filtered_tokens = [w for w in tokens if w not in STOPWORDS]
        overall_vocab.update(filtered_tokens)

        # 3. Sentiment scoring
        pos_count = sum(1 for w in filtered_tokens if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in filtered_tokens if w in NEGATIVE_WORDS)
        score = pos_count - neg_count
        sentiment_scores.append(score)

    avg_sentiment = sum(sentiment_scores) / max(1, len(sentiment_scores))
    top_5_words = overall_vocab.most_common(5)

    return {
        "documents_analyzed": num_documents,
        "total_tokens": total_tokens,
        "average_sentiment": round(avg_sentiment, 3),
        "top_keywords": top_5_words
    }


if __name__ == "__main__":
    print("Running Macro-Benchmark: Text NLP Analytics...")
    t0 = time.perf_counter()
    res = text_document_analysis(1200)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    print(f"  Analyzed {res['documents_analyzed']} documents ({res['total_tokens']} tokens) in {elapsed_ms:.2f} ms")
    print(f"  Top keywords: {res['top_keywords']}")
