from datetime import datetime

from agents.profile import AgentProfile
from simulation.engine import SimulationLog
from simulation.world_state import WorldState


async def generate_report(log: SimulationLog) -> str:
    ws = log.world_state
    agents = list(ws.agents.values())
    sections = _build_sections(log, agents, ws)
    return _assemble_markdown(log, sections)


def _build_sections(
    log: SimulationLog,
    agents: list[AgentProfile],
    ws: WorldState,
) -> dict[str, str]:
    return {
        "snapshot": _render_snapshot(log, agents, ws),
        "top_findings": _render_top_findings(log, agents, ws),
        "unexpected": _render_unexpected_outcomes(log, agents, ws),
        "trajectories": _render_trajectories(log, ws),
        "cascades": _render_cascades(log),
        "signals": _render_representative_signals(log, agents),
        "appendix": _render_appendix(log, ws),
    }


def _render_snapshot(log: SimulationLog, agents: list[AgentProfile], ws: WorldState) -> str:
    total_weight = sum(a.representational_weight for a in agents)
    emotional_counts: dict[str, int] = {}
    for agent in agents:
        emotional_counts[agent.emotional_state] = emotional_counts.get(agent.emotional_state, 0) + 1

    top_emotions = ", ".join(
        f"{emotion}={count}" for emotion, count in sorted(emotional_counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
    ) or "n/a"
    latest = ws.history[-1] if ws.history else None
    polarization = latest.political_polarization if latest else 0.0
    avg_stress = (
        sum(latest.economic_stress.values()) / len(latest.economic_stress)
        if latest and latest.economic_stress else 0.0
    )

    lines = [
        "## 1. Snapshot",
        "",
        f"- Theory: `{log.theory}`",
        f"- Time horizon: {log.steps_run} weeks",
        f"- Represented population: ~{total_weight * 1_000_000:,.0f}",
        f"- Final polarization: {polarization:.2f}",
        f"- Avg economic stress: {avg_stress:.2f}",
        f"- Dominant emotions: {top_emotions}",
        f"- Emergent events: {len(log.emergent_events)}",
        f"- Cascade traces: {len(log.cascades)}",
        "",
        "### Current World State",
        "",
        *(f"- {line[2:]}" if line.startswith("- ") else f"- {line}" for line in (log.current_world_state_summary or "Static archetype baseline.").splitlines()[:12]),
    ]
    return "\n".join(lines)


def _render_top_findings(log: SimulationLog, agents: list[AgentProfile], ws: WorldState) -> str:
    findings = _compute_top_findings(log, agents, ws)
    lines = ["## 2. Top Findings", ""]
    if not findings:
        lines.append("- No strong findings recorded.")
        return "\n".join(lines)
    for finding in findings:
        lines.append(f"- {finding}")
    return "\n".join(lines)


def _render_unexpected_outcomes(log: SimulationLog, agents: list[AgentProfile], ws: WorldState) -> str:
    items = _compute_unexpected_outcomes(log, agents, ws)
    lines = ["## 3. Unexpected Outcomes", ""]
    if not items:
        lines.append("- No clearly counterintuitive outcomes surfaced.")
        return "\n".join(lines)
    for item in items:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _render_trajectories(log: SimulationLog, ws: WorldState) -> str:
    trajectories = _compute_trajectories(log, ws)
    lines = ["## 4. Main Trajectories", ""]
    if not trajectories:
        lines.append("- No trajectory data recorded.")
        return "\n".join(lines)
    for item in trajectories:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _render_cascades(log: SimulationLog) -> str:
    if not log.cascades:
        return "## 5. Butterfly Effects\n\n- No cascade traces recorded.\n"

    lines = ["## 5. Butterfly Effects", ""]
    ranked = sorted(
        log.cascades,
        key=lambda c: (len(c.influenced_agents), len(c.edges)),
        reverse=True,
    )[:3]
    name_map = {agent.id: agent.name for agent in log.world_state.agents.values()}

    for idx, cascade in enumerate(ranked, start=1):
        lines.append(f"### Cascade {idx}: {cascade.origin_label} -> {cascade.topic}")
        lines.append(
            f"- Reach: {len(cascade.direct_recipients)} direct, {len(cascade.influenced_agents)} total, {len(cascade.edges)} activated edges"
        )
        lines.append("```mermaid")
        lines.append("graph LR")
        if cascade.edges:
            for edge in cascade.edges[:12]:
                source_label = name_map.get(edge.source_id, edge.source_id).replace('"', "'")
                target_label = name_map.get(edge.target_id, edge.target_id).replace('"', "'")
                lines.append(
                    f'  {edge.source_id}["{source_label}"] -->|h{edge.hop}:{edge.weight:.2f}| {edge.target_id}["{target_label}"]'
                )
        else:
            for agent_id in cascade.direct_recipients[:4]:
                label = name_map.get(agent_id, agent_id).replace('"', "'")
                lines.append(f'  {agent_id}["{label}"]')
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def _render_representative_signals(log: SimulationLog, agents: list[AgentProfile]) -> str:
    lines = ["## 6. Representative Signals", ""]
    selected = sorted(
        agents,
        key=lambda a: (
            len(a.decisions),
            a.change_fatigue + a.conflict_orientation + abs(a.political_ideology),
        ),
        reverse=True,
    )[:4]

    for agent in selected:
        memory = agent.memory[-1]["summary"] if agent.memory else "No significant memory recorded."
        lines.append(
            f"- {agent.name} ({agent.country}, {agent.occupation}, emotion={agent.emotional_state}) "
            f"-> {memory}"
        )

    return "\n".join(lines)


def _render_appendix(log: SimulationLog, ws: WorldState) -> str:
    lines = ["## 7. Appendix", "", "### World State Table", "", "```", ws.summary_table(), "```", ""]

    if log.emergent_events:
        lines.extend(["### Emergent Events", ""])
        for event in log.emergent_events[:8]:
            lines.append(
                f"- Week {event.step_introduced}: [{event.topic}] {event.description} (triggered by: {event.triggered_by})"
            )
        lines.append("")

    if log.conversations:
        lines.extend(["### Conversation Excerpts", ""])
        for conv in log.conversations[:3]:
            lines.append(f"- Week {conv.step}: {conv.agent_a} x {conv.agent_b} on `{conv.topic}`")
        lines.append("")

    return "\n".join(lines)


def _compute_top_findings(log: SimulationLog, agents: list[AgentProfile], ws: WorldState) -> list[str]:
    findings: list[str] = []
    latest = ws.history[-1] if ws.history else None
    if latest:
        findings.append(
            f"Polarization closed at `{latest.political_polarization:.2f}` with "
            f"`{_avg_stress(latest):.2f}` average economic stress, showing the system ended "
            f"in a {'tense' if latest.political_polarization >= 0.45 else 'contained'} equilibrium."
        )

    extreme_topics = _top_topic_swings(ws, limit=3)
    for topic, value in extreme_topics:
        direction = "support consolidated" if value > 0 else "backlash concentrated"
        findings.append(
            f"`{topic}` was a leading belief axis at `{value:+.2f}`, indicating where {direction}."
        )

    if log.emergent_events:
        event = log.emergent_events[0]
        findings.append(
            f"The first emergent event was `{event.topic}`, showing the simulation quickly translated individual reactions into collective consequences."
        )

    if log.cascades:
        biggest = max(log.cascades, key=lambda c: (len(c.influenced_agents), len(c.edges)))
        findings.append(
            f"The strongest butterfly effect came from `{biggest.origin_label}` on `{biggest.topic}`, reaching `{len(biggest.influenced_agents)}` agents through `{len(biggest.edges)}` activated edges."
        )

    return findings[:5]


def _compute_unexpected_outcomes(log: SimulationLog, agents: list[AgentProfile], ws: WorldState) -> list[str]:
    items: list[str] = []
    low_trust_hopeful = [a for a in agents if a.trust_in_institutions <= 0.25 and a.emotional_state in ("hopeful", "excited", "determined")]
    high_trust_anxious = [a for a in agents if a.trust_in_institutions >= 0.55 and a.emotional_state in ("anxious", "fearful", "angry")]
    if low_trust_hopeful:
        items.append(
            f"`{len(low_trust_hopeful)}` low-trust agents still ended hopeful or determined, suggesting outcomes were not driven by institutional confidence alone."
        )
    if high_trust_anxious:
        items.append(
            f"`{len(high_trust_anxious)}` relatively high-trust agents still ended anxious or angry, indicating the scenario destabilized even actors usually buffered by institutions."
        )

    cross_border = [
        c for c in log.cascades
        if any(
            log.world_state.agents[edge.source_id].country != log.world_state.agents[edge.target_id].country
            for edge in c.edges
        )
    ]
    if cross_border:
        items.append(
            f"`{len(cross_border)}` cascades crossed country boundaries, so the strongest effects were network-driven rather than strictly national."
        )

    extreme_disengagement = [a for a in agents if a.emotional_state == "resigned" and a.conflict_orientation >= 0.5]
    if extreme_disengagement:
        items.append(
            f"`{len(extreme_disengagement)}` agents became simultaneously combative and resigned, a more dangerous pattern than simple opposition because it mixes grievance with low faith in repair."
        )

    return items[:4]


def _compute_trajectories(log: SimulationLog, ws: WorldState) -> list[str]:
    trajectories: list[str] = []
    latest = ws.history[-1] if ws.history else None
    if not latest:
        return trajectories

    for topic, value in _top_topic_swings(ws, limit=3):
        trend = _topic_trend(ws, topic)
        if trend is None:
            continue
        trajectories.append(
            f"`{topic}` moved from `{trend[0]:+.2f}` to `{trend[1]:+.2f}` and finished at `{value:+.2f}`, making it one of the clearest scenario trajectories."
        )

    if latest.cascade_summaries:
        trajectories.append(
            f"Late-stage network activity was still active: {latest.cascade_summaries[0]}."
        )

    return trajectories[:4]


def _top_topic_swings(ws: WorldState, limit: int = 3) -> list[tuple[str, float]]:
    latest = ws.history[-1] if ws.history else None
    if not latest:
        return []
    global_topics: dict[str, float] = {}
    for seg_beliefs in latest.opinion_by_segment.values():
        for topic, value in seg_beliefs.items():
            canonical = _canonical_topic(topic)
            global_topics.setdefault(canonical, []).append(value)
    scored = [(topic, sum(values) / len(values)) for topic, values in global_topics.items()]
    scored.sort(key=lambda kv: abs(kv[1]), reverse=True)
    return scored[:limit]


def _topic_trend(ws: WorldState, topic: str) -> tuple[float, float] | None:
    values: list[float] = []
    for snap in ws.history:
        per_step: list[float] = []
        for seg_beliefs in snap.opinion_by_segment.values():
            for raw_topic, value in seg_beliefs.items():
                if _canonical_topic(raw_topic) == topic:
                    per_step.append(value)
        if per_step:
            values.append(sum(per_step) / len(per_step))
    if len(values) >= 2:
        return values[0], values[-1]
    if len(values) == 1:
        return values[0], values[0]
    return None


def _canonical_topic(topic: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "_" for ch in topic)
    normalized = "_".join(part for part in normalized.split("_") if part)

    aliases = {
        "government_policies": "government_policy",
        "government_policy": "government_policy",
        "economic_policies": "economic_policy",
        "economic_policy": "economic_policy",
        "economic_impact": "economic_impact",
        "globaleconomy": "global_economy",
        "global_economy": "global_economy",
        "communityprotests": "community_protests",
        "oppositionarguments": "opposition_arguments",
        "futureofwork": "future_of_work",
        "localbusinesses": "local_businesses",
    }
    topic_key = aliases.get(normalized, normalized)
    return topic_key.replace("_", " ")


def _avg_stress(snapshot) -> float:
    return (
        sum(snapshot.economic_stress.values()) / len(snapshot.economic_stress)
        if snapshot.economic_stress else 0.0
    )


def _assemble_markdown(log: SimulationLog, sections: dict[str, str]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""# The Small World — Findings Report

**Theory:** {log.theory}
**Simulated:** {log.steps_run} weeks
**Generated:** {now}

---

{sections['snapshot']}

---

{sections['top_findings']}

---

{sections['unexpected']}

---

{sections['trajectories']}

---

{sections['cascades']}

---

{sections['signals']}

---

{sections['appendix']}

---

*Generated by The Small World — a current-state-grounded scenario engine.*
"""
