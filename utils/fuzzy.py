import re
from difflib import SequenceMatcher, get_close_matches


def normalize_text(value):
    if value is None:
        return ""
    text = str(value).strip().lower().replace("\\", "/")
    text = re.sub(r"['\"`]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def similarity(a, b):
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def best_match(query, choices, cutoff=0.78):
    if not choices:
        return None, 0.0

    normalized = {normalize_text(choice): choice for choice in choices}
    query_norm = normalize_text(query)

    if query_norm in normalized:
        return normalized[query_norm], 1.0

    close = get_close_matches(query_norm, list(normalized.keys()), n=1, cutoff=cutoff)
    if close:
        key = close[0]
        return normalized[key], similarity(query_norm, key)

    best_choice = None
    best_score = 0.0
    for choice in choices:
        score = similarity(query_norm, choice)
        if score > best_score:
            best_choice = choice
            best_score = score

    if best_score >= cutoff:
        return best_choice, best_score
    return None, 0.0


def fuzzy_prefix(text, phrase, cutoff=0.78):
    text_words = normalize_text(text).split()
    phrase_words = normalize_text(phrase).split()
    if len(text_words) < len(phrase_words):
        return False, ""

    prefix = " ".join(text_words[: len(phrase_words)])
    remainder = " ".join(text_words[len(phrase_words):]).strip()
    return similarity(prefix, phrase) >= cutoff, remainder
