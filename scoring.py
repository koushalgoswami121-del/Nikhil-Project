"""Lightweight answer scoring (no scikit-learn / scipy required)."""

import re
from math import log, sqrt


def _tokenize(text):
    return re.findall(r"\b\w+\b", (text or "").lower())


def _tfidf_vectors(docs):
    n = len(docs)
    df = {}
    for doc in docs:
        for term in set(doc):
            df[term] = df.get(term, 0) + 1
    vectors = []
    for doc in docs:
        tf = {}
        for term in doc:
            tf[term] = tf.get(term, 0) + 1
        vec = {}
        for term, count in tf.items():
            idf = log((n + 1) / (df.get(term, 0) + 1)) + 1
            vec[term] = count * idf
        vectors.append(vec)
    return vectors


def _cosine_similarity(vec_a, vec_b):
    keys = set(vec_a) | set(vec_b)
    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in keys)
    mag_a = sqrt(sum(v * v for v in vec_a.values()))
    mag_b = sqrt(sum(v * v for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def answer_similarity_score(reference, answer):
    """Return 0–100 similarity between model answer and user answer."""
    docs = [_tokenize(reference), _tokenize(answer)]
    if not docs[0] or not docs[1]:
        return 0
    vecs = _tfidf_vectors(docs)
    return round(float(_cosine_similarity(vecs[0], vecs[1])) * 100)
