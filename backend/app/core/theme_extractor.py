"""
core/theme_extractor.py
=======================
Extracts meaningful keywords per sentiment group using TF-IDF.
"""

import re
from collections import Counter
import numpy as np

STOPWORDS = {
    "the","is","in","it","of","and","to","a","an","that","this","was","for",
    "on","are","with","as","at","be","by","from","or","but","not","have",
    "had","he","she","they","we","you","i","my","your","our","their","its",
    "will","would","could","should","do","did","does","has","been","were",
    "which","who","what","when","where","how","all","just","about","up",
    "course","class","professor","faculty","student","lecture","semester",
    "also","very","really","quite","much","many","lot","some","more","most",
    "than","then","so","if","no","yes","please","think","feel","believe",
    "make","get","go","take","see","know","need","one","two","three","us",
    "them","there","here","back","good","bad","subject","topic"
}


def clean(text: str) -> str:
    text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    return re.sub(r'\s+', ' ', text).strip()


def extract_keywords(texts: list, top_n: int = 10) -> list:
    if not texts or len(texts) < 1:
        return []

    cleaned = [clean(t) for t in texts if len(t.split()) > 1]
    if not cleaned:
        return []

    all_words = []
    for t in cleaned:
        all_words.extend([w for w in t.split() if w not in STOPWORDS and len(w) > 3])
    freq_map = Counter(all_words)

    if len(cleaned) < 2:
        return [{"keyword": w, "score": round(c / max(len(all_words), 1), 4), "frequency": c}
                for w, c in freq_map.most_common(top_n)]

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vec = TfidfVectorizer(
            stop_words=list(STOPWORDS),
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            max_features=300
        )
        matrix = vec.fit_transform(cleaned)
        features = vec.get_feature_names_out()
        scores = np.asarray(matrix.sum(axis=0)).flatten()
        top_idx = scores.argsort()[::-1]

        results, seen = [], set()
        for idx in top_idx:
            word = features[idx]
            if word in seen or len(word) < 3:
                continue
            if all(w in STOPWORDS for w in word.split()):
                continue
            seen.add(word)
            results.append({
                "keyword": word,
                "score": round(float(scores[idx]), 4),
                "frequency": freq_map.get(word, 1)
            })
            if len(results) >= top_n:
                break
        return results
    except Exception:
        return [{"keyword": w, "score": round(c / max(len(all_words), 1), 4), "frequency": c}
                for w, c in freq_map.most_common(top_n)]


def extract_themes(results: list) -> dict:
    """Split by sentiment and extract keywords for each group + all."""
    groups = {"POSITIVE": [], "NEGATIVE": [], "NEUTRAL": [], "ALL": []}
    for r in results:
        label = r.get("sentiment", "NEUTRAL")
        text = r.get("text", "")
        groups[label].append(text)
        groups["ALL"].append(text)

    return {label: extract_keywords(texts, top_n=10) for label, texts in groups.items()}
