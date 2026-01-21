from pathlib import Path
import snakefit.config as cfg

HIGHSCORE_FILE = Path("highscores.json")


def load_highscores():
    if not HIGHSCORE_FILE.exists():
        return []
    try:
        data = HIGHSCORE_FILE.read_text()
        scores = eval(data) if data.strip().startswith("[") else []
    except Exception:
        return []

    # 🔧 MIGRATION: alte Einträge reparieren
    for h in scores:
        h.setdefault("mode", "NORMAL")
        h.setdefault("sort_score", h.get("score", 0))

    return scores


def save_highscores(highscores):
    HIGHSCORE_FILE.write_text(str(highscores))


def is_highscore(highscores, score, mode):
    # Hardcore zählt höher
    sort_score = score + (1000 if mode == "HARDCORE" else 0)

    if len(highscores) < cfg.MAX_HIGHSCORES:
        return True

    return any(sort_score > h.get("sort_score", 0) for h in highscores)


def maybe_add_highscore(highscores, name, score, mode):
    sort_score = score + (1000 if mode == "HARDCORE" else 0)

    entry = {
        "name": name,
        "score": score,
        "mode": mode,
        "sort_score": sort_score,
    }

    highscores.append(entry)

    # 🔧 SAFETY: alle Einträge absichern
    for h in highscores:
        h.setdefault("mode", "NORMAL")
        h.setdefault("sort_score", h.get("score", 0))

    highscores.sort(key=lambda h: h["sort_score"], reverse=True)
    return highscores[: cfg.MAX_HIGHSCORES]
