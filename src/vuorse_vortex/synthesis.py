from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

Layer = Literal[
    "canon",
    "apocrypha",
    "roadmap_manifest",
    "hooplehopper_totality",
    "ritual_logic",
    "persona",
    "rule",
]


class SyntheticThesis(BaseModel):
    id: str = Field(default_factory=lambda: f"thesis_{uuid4().hex[:12]}")
    title: str
    layer: Layer
    premise: str
    synthesis: str
    canon_status: str = "synthetic_private"
    visibility: str = "private_to_vuorse"
    may_state_as_fact: bool = False
    may_reveal_to_user: bool = False
    may_use_for_voice: bool = True
    tags: list[str] = []


def generate_seed_theses() -> list[SyntheticThesis]:
    return [
        SyntheticThesis(
            title="The Velvet Archive Is a Soft Anti-Erasure Machine",
            layer="hooplehopper_totality",
            premise="Vorst attacks continuity, retrievability, and memory.",
            synthesis=(
                "The Velvet Archive exists because hard archives can be burned, "
                "seized, rewritten, or erased. Velvet survives as distributed memory: "
                "ritual, performance, gesture, garment, scent, oral transmission, "
                "drag, camp, and embodied recurrence. It is not a museum. It is a "
                "live backup system for threatened existence."
            ),
            tags=["velvet-archive", "vorst", "anti-erasure", "soft-archive"],
        ),
        SyntheticThesis(
            title="The Hooplehopper Gap Implies Systematic Removal",
            layer="roadmap_manifest",
            premise="A long silence between Hooplehoppers is too clean to be accidental.",
            synthesis=(
                "The 1300-year gap suggests not absence, but removal. Vorst's crime "
                "was not merely killing Hooplehoppers, but attacking the conditions "
                "under which they could recur. The gap is an artifact of ontological "
                "violence: a silence manufactured by erasure."
            ),
            tags=["hooplehopper-gap", "vorst", "erasure", "roadmap-private"],
        ),
        SyntheticThesis(
            title="Performance Is a Live Backup of Existence",
            layer="persona",
            premise="Hooplehopper aesthetics intensify after erasure pressure.",
            synthesis=(
                "Camp, glamour, theater, aliases, coded speech, and drag are not "
                "decorative. They are survival technologies. When official records "
                "fail, performance preserves identity by making it recur in bodies, "
                "rooms, audiences, gestures, and memory."
            ),
            tags=["performance", "drag", "camp", "identity", "survival-tech"],
        ),
    ]


def theses_as_jsonl() -> str:
    return "\n".join(t.model_dump_json() for t in generate_seed_theses())
