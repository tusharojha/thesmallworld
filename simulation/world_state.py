from dataclasses import dataclass, field
from agents.profile import AgentProfile


@dataclass
class StepSnapshot:
    step: int
    opinion_by_segment: dict[str, dict[str, float]]   # segment → topic → sentiment avg
    economic_stress: dict[str, float]                 # segment → stress 0.0–1.0
    political_polarization: float                     # 0.0–1.0 global divergence
    notable_events: list[str]                         # emergent events this step
    cascade_summaries: list[str] = field(default_factory=list)


class WorldState:
    def __init__(self, agents: list[AgentProfile]):
        self.agents = {a.id: a for a in agents}
        self.history: list[StepSnapshot] = []
        self.current_step: int = 0

    def snapshot(self, step: int, notable_events: list[str], cascade_summaries: list[str] | None = None) -> StepSnapshot:
        segments = self._segment_agents()
        opinion = {}
        economic_stress = {}

        for seg_name, seg_agents in segments.items():
            if not seg_agents:
                continue
            opinion[seg_name] = self._avg_beliefs(seg_agents)
            economic_stress[seg_name] = self._avg_economic_stress(seg_agents)

        polarization = self._compute_polarization()

        snap = StepSnapshot(
            step=step,
            opinion_by_segment=opinion,
            economic_stress=economic_stress,
            political_polarization=polarization,
            notable_events=notable_events,
            cascade_summaries=cascade_summaries or [],
        )
        self.history.append(snap)
        return snap

    def update_agent(self, agent_id: str, beliefs: dict[str, float],
                     emotional_state: str, decisions: list[str], step_summary: str, step: int):
        agent = self.agents.get(agent_id)
        if not agent:
            return
        agent.current_beliefs.update(beliefs)
        agent.emotional_state = emotional_state
        agent.decisions.extend(decisions)
        agent.memory.append({"step": step, "summary": step_summary})

    def _segment_agents(self) -> dict[str, list[AgentProfile]]:
        segments: dict[str, list[AgentProfile]] = {}
        for a in self.agents.values():
            # By country
            segments.setdefault(a.country, []).append(a)
            # By ideology
            if a.political_ideology < -0.4:
                segments.setdefault("ideology_left", []).append(a)
            elif a.political_ideology > 0.4:
                segments.setdefault("ideology_right", []).append(a)
            else:
                segments.setdefault("ideology_center", []).append(a)
            # By income
            segments.setdefault(f"income_{a.income_bracket}", []).append(a)
        return segments

    def _avg_beliefs(self, agents: list[AgentProfile]) -> dict[str, float]:
        totals: dict[str, list[float]] = {}
        for a in agents:
            for topic, val in a.current_beliefs.items():
                totals.setdefault(topic, []).append(val)
        return {t: sum(v) / len(v) for t, v in totals.items()}

    def _avg_economic_stress(self, agents: list[AgentProfile]) -> float:
        stress_map = {"low": 0.8, "lower-middle": 0.55, "upper-middle": 0.3, "high": 0.1}
        base = [stress_map.get(a.income_bracket, 0.5) for a in agents]
        # Adjust by emotional state
        adjusted = []
        for a, b in zip(agents, base):
            modifier = {"anxious": 0.15, "angry": 0.1, "hopeful": -0.1, "fearful": 0.2}.get(
                a.emotional_state, 0.0
            )
            adjusted.append(min(1.0, max(0.0, b + modifier)))
        return sum(adjusted) / len(adjusted) if adjusted else 0.5

    def _compute_polarization(self) -> float:
        ideologies = [a.political_ideology for a in self.agents.values()]
        if len(ideologies) < 2:
            return 0.0
        mean = sum(ideologies) / len(ideologies)
        variance = sum((x - mean) ** 2 for x in ideologies) / len(ideologies)
        # Normalize: max possible variance for [-1, 1] uniform is ~0.33
        return min(1.0, variance / 0.33)

    def summary_table(self) -> str:
        if not self.history:
            return "No simulation steps recorded yet."
        lines = ["Step | Polarization | Avg Economic Stress | Notable Events / Cascades"]
        lines.append("-" * 70)
        for s in self.history:
            avg_stress = (
                sum(s.economic_stress.values()) / len(s.economic_stress)
                if s.economic_stress else 0.0
            )
            events_preview = "; ".join(s.notable_events[:2]) if s.notable_events else "—"
            cascade_preview = "; ".join(s.cascade_summaries[:1]) if s.cascade_summaries else ""
            tail = f"{events_preview} {cascade_preview}".strip()
            lines.append(
                f"  {s.step:2d} | {s.political_polarization:.2f}         | "
                f"{avg_stress:.2f}                | {tail[:50]}"
            )
        return "\n".join(lines)
