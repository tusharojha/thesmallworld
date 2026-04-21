from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentProfile:
    # Identity
    id: str
    name: str

    # Demographics
    age: int
    gender: str                   # male / female / non-binary
    country: str
    city_type: str                # urban / suburban / rural
    income_bracket: str           # low / lower-middle / upper-middle / high
    education_level: str          # none / primary / secondary / tertiary / postgrad
    occupation: str

    # Worldview
    political_ideology: float     # -1.0 (far-left) to 1.0 (far-right)
    religious_affiliation: str    # atheist / christian / muslim / hindu / buddhist / other
    religiosity_level: float      # 0.0 (secular) to 1.0 (devout)
    trust_in_institutions: float  # 0.0 (no trust) to 1.0 (full trust)
    openness_to_change: float     # 0.0 (resistant) to 1.0 (welcoming)

    # Personality — Big Five (0.0–1.0 each)
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float

    # Friction / realism traits
    media_trust: float = 0.5      # 0.0 (believes almost nothing) to 1.0 (generally trusts reporting)
    political_efficacy: float = 0.5  # 0.0 (no voice) to 1.0 (feels influential)
    change_fatigue: float = 0.5   # 0.0 (fresh) to 1.0 (overloaded by disruption)
    conflict_orientation: float = 0.5  # 0.0 (avoidant) to 1.0 (combative)
    social_trust: float = 0.5     # 0.0 (suspicious of others) to 1.0 (generally trusting)
    status_quo_bias: float = 0.5  # 0.0 (wants upheaval) to 1.0 (prefers continuity)

    # Social
    social_connections: list[str] = field(default_factory=list)   # other agent ids
    media_sources: list[str] = field(default_factory=list)        # e.g. ["mainstream_tv", "social_media", "local_radio"]

    # Simulation state (mutable during run)
    memory: list[dict] = field(default_factory=list)              # recent events this agent experienced
    current_beliefs: dict[str, float] = field(default_factory=dict)  # topic → sentiment (-1 to 1)
    emotional_state: str = "neutral"
    decisions: list[str] = field(default_factory=list)            # notable decisions made

    # Population weight — how many real humans this archetype represents (millions)
    representational_weight: int = 1

    def short_bio(self) -> str:
        ideology_label = (
            "far-left" if self.political_ideology < -0.6 else
            "left-leaning" if self.political_ideology < -0.2 else
            "centrist" if self.political_ideology < 0.2 else
            "right-leaning" if self.political_ideology < 0.6 else
            "far-right"
        )
        return (
            f"{self.name}, {self.age}-year-old {self.gender} from {self.city_type} {self.country}. "
            f"Occupation: {self.occupation}. Income: {self.income_bracket}. "
            f"Education: {self.education_level}. {ideology_label.capitalize()} politically. "
            f"Religion: {self.religious_affiliation} (religiosity {self.religiosity_level:.1f}). "
            f"Trust in institutions: {self.trust_in_institutions:.1f}. "
            f"Media trust: {self.media_trust:.1f}. Political efficacy: {self.political_efficacy:.1f}. "
            f"Change fatigue: {self.change_fatigue:.1f}. Conflict orientation: {self.conflict_orientation:.1f}. "
            f"Status quo bias: {self.status_quo_bias:.1f}. Media: {', '.join(self.media_sources)}."
        )

    def personality_summary(self) -> str:
        return (
            f"Personality — Openness: {self.openness:.1f}, Conscientiousness: {self.conscientiousness:.1f}, "
            f"Extraversion: {self.extraversion:.1f}, Agreeableness: {self.agreeableness:.1f}, "
            f"Neuroticism: {self.neuroticism:.1f}. Social trust: {self.social_trust:.1f}."
        )

    def memory_context(self, last_n: int = 5) -> str:
        recent = self.memory[-last_n:] if self.memory else []
        if not recent:
            return "No prior events experienced in this simulation."
        lines = [f"- Week {e['step']}: {e['summary']}" for e in recent]
        return "Recent experiences:\n" + "\n".join(lines)
