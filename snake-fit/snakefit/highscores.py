import json
from pathlib import Path
import snakefit.config as cfg


def load_highscores():
    path = Path(cfg.HIGHSCORE_FILE)

    if not path.exists():
        return []

    with open(path, "r") as f:
        data = json.load(f)

    # --- Migration: old single-score format ---
    if isinstance(data, dict) and "name" in data and "score" in data:
        return [data]

    # --- Correct format: list of scores ---
    if isinstance(data, list):
        # Filter invalid entries
        cleaned = []
        for entry in data:
            if isinstance(entry, dict) and "name" in entry and "score" in entry:
                cleaned.append(entry)
        return cleaned[:10]

    # Fallback
    return []


def save_highscores(scores):
    with open(cfg.HIGHSCORE_FILE, "w") as f:
        json.dump(scores[:10], f, indent=2)


def maybe_add_highscore(scores, name, score):
    scores.append({"name": name, "score": score})
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:10]


def is_highscore(scores, score):
    if len(scores) < 10:
        return True
    return score > scores[-1]["score"]