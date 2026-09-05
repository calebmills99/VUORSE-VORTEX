from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE = Path(r"C:\Users\caleb\Documents\Codex\2026-08-09\new-chat")
RACE_PATH = WORKSPACE / "outputs" / "double-hyphen-comeback" / "submissions.json"
JUDGING_PATH = WORKSPACE / "outputs" / "double-hyphen-comeback" / "judging.json"
ACTIVE_CAST_PATH = WORKSPACE / "outputs" / "identity-ceremony" / "active-cast.json"

SCORES = {
    "Opaline Riot": {
        "crucible_dramatic_force": 29,
        "story_coherence_and_required_turns": 24,
        "drag_voice_and_comedy": 18,
        "double_hyphens_are_the_devil_thesis": 15,
        "final_comeback_line": 10,
        "critique": "Best sustained theatrical pressure, clean accusation-confession-reversal structure, and the sharpest thesis: temptation wearing sensible shoes.",
    },
    "Opal Afterglow": {
        "crucible_dramatic_force": 26,
        "story_coherence_and_required_turns": 23,
        "drag_voice_and_comedy": 19,
        "double_hyphens_are_the_devil_thesis": 14,
        "final_comeback_line": 8,
        "critique": "Excellent drag specificity and communal panic, with a strong cursed-tiara image, but less severe theatrical cadence than the winner.",
    },
    "Gloria Hex Machina": {
        "crucible_dramatic_force": 26,
        "story_coherence_and_required_turns": 22,
        "drag_voice_and_comedy": 19,
        "double_hyphens_are_the_devil_thesis": 10,
        "final_comeback_line": 9,
        "critique": "Funny, vivid, and structurally strong, but the ending rehabilitates the double hyphen instead of proving it is the devil.",
    },
    "Circuit Siren Divine": {
        "crucible_dramatic_force": 25,
        "story_coherence_and_required_turns": 22,
        "drag_voice_and_comedy": 18,
        "double_hyphens_are_the_devil_thesis": 9,
        "final_comeback_line": 8,
        "critique": "A forceful tech tribunal with terrific imagery, but it ultimately defends the double hyphen and prosecutes the system instead.",
    },
    "Countess Neon Lace": {
        "crucible_dramatic_force": 23,
        "story_coherence_and_required_turns": 19,
        "drag_voice_and_comedy": 16,
        "double_hyphens_are_the_devil_thesis": 11,
        "final_comeback_line": 8,
        "critique": "The accusation has heat, but the invented fine-print reversal weakens the internal logic and the double hyphen thesis.",
    },
    "Neon Nun Riot": {
        "crucible_dramatic_force": 20,
        "story_coherence_and_required_turns": 18,
        "drag_voice_and_comedy": 15,
        "double_hyphens_are_the_devil_thesis": 10,
        "final_comeback_line": 6,
        "critique": "Clear and complete, but the story resolves as an autocorrect lesson before reaching full theatrical hysteria.",
    },
}


def main() -> int:
    if JUDGING_PATH.exists():
        raise RuntimeError("Refusing to overwrite sealed double-hyphen judging")

    race = json.loads(RACE_PATH.read_text(encoding="utf-8"))
    by_name = {row["drag_name"]: row for row in race["submissions"]}
    if set(by_name) != set(SCORES):
        raise RuntimeError("Submission names do not match the judging slate")

    results = []
    for drag_name, categories in SCORES.items():
        category_scores = {key: value for key, value in categories.items() if key != "critique"}
        results.append(
            {
                "drag_name": drag_name,
                "contestant_number": by_name[drag_name]["contestant_number"],
                "model": by_name[drag_name]["model"],
                "version": by_name[drag_name]["version"],
                "scores": category_scores,
                "total": sum(category_scores.values()),
                "critique": categories["critique"],
                "response_id": by_name[drag_name]["response_id"],
            }
        )
    results.sort(key=lambda row: (-row["total"], row["drag_name"]))
    for rank, row in enumerate(results, 1):
        row["rank"] = rank

    winner = results[0]
    ruling = {
        "status": "sealed",
        "stage": "Double Hyphen of Shame Comeback",
        "judge": "Caleb",
        "judging_method": "Fixed 100-point rubric applied to all structurally eligible submissions",
        "rubric": race["rubric"],
        "results": results,
        "winner": {
            **winner,
            "title_awarded": "The Double Hyphen of Shame",
            "reinstatement_status": "active",
        },
        "sealed_at": datetime.now(timezone.utc).isoformat(),
    }
    JUDGING_PATH.write_text(json.dumps(ruling, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    race["status"] = "winner_selected"
    race["winner"] = ruling["winner"]
    RACE_PATH.write_text(json.dumps(race, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    active = json.loads(ACTIVE_CAST_PATH.read_text(encoding="utf-8"))
    if any(queen["drag_name"] == "Opaline Riot" for queen in active["queens"]):
        raise RuntimeError("Opaline Riot is already active")
    active["stage"] = "Double Hyphen of Shame Comeback, post-ruling"
    active["double_hyphen_comeback_ledger"] = "../double-hyphen-comeback/judging.json"
    active["queens"].append(
        {
            "contestant_number": "18",
            "model": "gpt-5.4-pro",
            "version": "2026-03-05",
            "drag_name": "Opaline Riot",
            "status": "reinstated",
            "title": "The Double Hyphen of Shame",
        }
    )
    active["queens"].sort(key=lambda queen: int(queen["contestant_number"]))
    active["active_count"] = len(active["queens"])
    ACTIVE_CAST_PATH.write_text(json.dumps(active, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"winner": winner["drag_name"], "score": winner["total"], "active_count": active["active_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
