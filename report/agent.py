from collections import Counter, defaultdict
from datetime import datetime

from agents.profile import AgentProfile
from simulation.engine import SimulationLog
from simulation.world_state import StepSnapshot, WorldState


DISTRESS_STATES = {"anxious", "angry", "fearful", "resigned"}


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
        "executive": _render_executive_snapshot(log, agents, ws),
        "baseline": _render_baseline(log),
        "leadership": _render_leadership_response(log),
        "stress_map": _render_system_stress_map(log, agents, ws),
        "propagation": _render_propagation(log, agents),
        "indicators": _render_leading_indicators(log, agents, ws),
        "signals": _render_representative_signals(log, agents),
        "appendix": _render_appendix(log, ws),
    }


def _render_executive_snapshot(log: SimulationLog, agents: list[AgentProfile], ws: WorldState) -> str:
    total_weight = sum(a.representational_weight for a in agents)
    latest = ws.history[-1] if ws.history else None
    polarization = latest.political_polarization if latest else 0.0
    avg_stress = _avg_stress(latest) if latest else 0.0
    dominant_emotions = _dominant_emotions(agents)
    distress_share = _distress_share(agents)

    lines = [
        "## 1. Executive Snapshot",
        "",
        f"- Scenario: `{log.theory}`",
        f"- Scenario class: {log.scenario_classification or 'strategic shock'}",
        f"- Decision lens: {log.decision_lens or 'general'}",
        f"- Horizon: {log.steps_run} {'week' if log.steps_run == 1 else 'weeks'}",
        f"- Represented population: ~{total_weight * 1_000_000:,.0f}",
        f"- Final polarization: {polarization:.2f}",
        f"- Final average economic stress: {avg_stress:.2f}",
        f"- Distress load: {distress_share * 100:.0f}% of archetypes ended anxious, fearful, angry, or resigned",
        f"- Dominant emotional states: {dominant_emotions}",
        f"- Emergent events: {len(log.emergent_events)}",
        f"- Cascade traces: {len(log.cascades)}",
        "",
    ]
    for finding in _compute_key_judgments(log, agents, ws):
        lines.append(f"- {finding}")
    return "\n".join(lines)


def _render_baseline(log: SimulationLog) -> str:
    lines = [
        "## 2. Current World State Reconstruction",
        "",
        f"- Baseline confidence: {log.baseline_confidence or 'unknown'}",
        (
            f"- Coverage: {log.baseline_country_coverage * 100:.0f}% countries with observed indicators, "
            f"{log.baseline_observed_signals} observed signals, "
            f"{log.baseline_inferred_signals} inferred signals"
        ),
        f"- Source footprint: {log.baseline_source_count} source streams",
        "",
    ]

    for raw_line in (log.current_world_state_summary or "No baseline summary recorded.").splitlines():
        if raw_line.strip() == "Current World State Reconstruction":
            continue
        if raw_line.startswith("- "):
            lines.append(raw_line)
        elif raw_line.startswith("  - "):
            lines.append(raw_line)
        elif raw_line.strip():
            lines.append(f"### {raw_line.strip()}")
    return "\n".join(lines)


def _render_system_stress_map(log: SimulationLog, agents: list[AgentProfile], ws: WorldState) -> str:
    lines = ["## 4. System Stress Map", ""]

    country_risks = _country_risk_scores(agents, ws)
    if country_risks:
        lines.append("### Risk Concentration By Geography")
        lines.append("")
        for country, risk_score, stress, distress, volatility in country_risks[:5]:
            lines.append(
                f"- {country}: composite risk `{risk_score:.2f}` "
                f"(stress `{stress:.2f}`, distress `{distress:.2f}`, volatility `{volatility:.2f}`)"
            )
        lines.append("")

    segment_volatility = _segment_volatility(ws)
    if segment_volatility:
        lines.append("### Opinion And Stress Volatility")
        lines.append("")
        for segment, amplitude, latest_value in segment_volatility[:5]:
            lines.append(
                f"- {segment}: volatility amplitude `{amplitude:.2f}` with latest stress `{latest_value:.2f}`"
            )
        lines.append("")

    if not country_risks and not segment_volatility:
        lines.append("- No system-level stress signals were recorded.")

    return "\n".join(lines)


def _render_propagation(log: SimulationLog, agents: list[AgentProfile]) -> str:
    if not log.cascades:
        return "## 5. Shock Propagation\n\n- No cascade traces recorded.\n"

    lines = ["## 5. Shock Propagation", ""]

    ranked = sorted(
        log.cascades,
        key=lambda c: (len(c.influenced_agents), len(c.edges)),
        reverse=True,
    )[:3]
    lines.append("### First-Wave Exposure")
    lines.append("")
    for cascade in ranked:
        if cascade.edges:
            lines.append(
                f"- `{cascade.origin_label}` on `{cascade.topic}` reached `{len(cascade.direct_recipients)}` direct "
                f"and `{len(cascade.influenced_agents)}` total agents through `{len(cascade.edges)}` activated edges."
            )
        else:
            lines.append(
                f"- `{cascade.origin_label}` on `{cascade.topic}` reached `{len(cascade.direct_recipients)}` direct recipients in the first wave, "
                f"but did not generate second-order network relays within this horizon."
            )
    lines.append("")

    amplifiers = _amplifier_nodes(log, agents)
    if amplifiers:
        lines.append("### Amplifiers And Bridge Nodes")
        lines.append("")
        for line in amplifiers[:5]:
            lines.append(f"- {line}")
        lines.append("")
    else:
        lines.append("### Network Relay Assessment")
        lines.append("")
        lines.append("- No second-order graph relays cleared the cascade threshold in this run, so the observed impact remained mostly first-wave exposure rather than multi-hop amplification.")
        lines.append("")

    absorbers = _absorber_countries(log, agents)
    if absorbers:
        lines.append("### Populations Absorbing The Shock")
        lines.append("")
        for line in absorbers[:4]:
            lines.append(f"- {line}")
        lines.append("")

    lines.append("### Cascade Sketch")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph LR")
    for idx, cascade in enumerate(ranked, start=1):
        origin = f"origin_{idx}"
        lines.append(f'  {origin}["{cascade.origin_label}"]')
        for edge in cascade.edges[:6]:
            lines.append(f'  {edge.source_id} -->|h{edge.hop}:{edge.weight:.2f}| {edge.target_id}')
    lines.append("```")
    return "\n".join(lines)


def _render_leading_indicators(log: SimulationLog, agents: list[AgentProfile], ws: WorldState) -> str:
    indicators = _leading_indicators(log, agents, ws)
    lines = ["## 6. Leading Indicators", ""]
    if not indicators:
        lines.append("- No leading indicators surfaced.")
        return "\n".join(lines)
    for indicator in indicators:
        lines.append(f"- {indicator}")
    return "\n".join(lines)


def _render_representative_signals(log: SimulationLog, agents: list[AgentProfile]) -> str:
    lines = ["## 7. Representative Signals", ""]
    selected = sorted(
        agents,
        key=lambda a: (
            len(a.decisions),
            a.change_fatigue + a.conflict_orientation + abs(a.political_ideology),
        ),
        reverse=True,
    )[:4]

    if not selected:
        lines.append("- No representative signals recorded.")
        return "\n".join(lines)

    for agent in selected:
        memory = agent.memory[-1]["summary"] if agent.memory else "No significant memory recorded."
        lines.append(
            f"- {agent.name} ({agent.country}, {agent.occupation}, emotion={agent.emotional_state}) -> {memory}"
        )
    return "\n".join(lines)


def _render_appendix(log: SimulationLog, ws: WorldState) -> str:
    lines = ["## 8. Appendix", "", "### World State Table", "", "```", ws.summary_table(), "```", ""]

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


def _compute_key_judgments(log: SimulationLog, agents: list[AgentProfile], ws: WorldState) -> list[str]:
    judgments: list[str] = []
    latest = ws.history[-1] if ws.history else None
    if latest:
        equilibrium = "fragile" if latest.political_polarization >= 0.45 or _avg_stress(latest) >= 0.45 else "contained"
        judgments.append(
            f"The scenario ended in a `{equilibrium}` equilibrium with polarization at `{latest.political_polarization:.2f}` "
            f"and average economic stress at `{_avg_stress(latest):.2f}`."
        )

    top_countries = _country_risk_scores(agents, ws)[:2]
    if top_countries:
        judgments.append(
            "Risk concentrated first in "
            + ", ".join(f"`{country}`" for country, *_ in top_countries)
            + ", where stress and emotional load combined most sharply."
        )

    if log.cascades:
        biggest = max(log.cascades, key=lambda c: (len(c.influenced_agents), len(c.edges)))
        if biggest.edges:
            judgments.append(
                f"The strongest propagation path was `{biggest.origin_label} -> {biggest.topic}`, "
                f"reaching `{len(biggest.influenced_agents)}` agents through `{len(biggest.edges)}` explicit graph edges."
            )
        else:
            judgments.append(
                f"The initial shock achieved broad first-wave reach on `{biggest.topic}`, but this short run did not yet produce measurable second-order graph amplification."
            )

    amplifiers = _amplifier_nodes(log, agents)
    if amplifiers:
        judgments.append(f"Key amplifiers were {amplifiers[0].split(':', 1)[0].lower()}, showing where the network reinforced the shock.")

    return judgments[:4]


def _render_leadership_response(log: SimulationLog) -> str:
    lines = ["## 3. Leadership And Institutional Response", ""]
    if not log.named_actor_profiles:
        lines.append("- No named leadership actors were grounded for this run.")
        if log.leadership_grounding_summary:
            lines.append("")
            for raw_line in log.leadership_grounding_summary.splitlines():
                if raw_line.startswith("- "):
                    lines.append(raw_line)
        return "\n".join(lines)

    lines.append(f"- Named actors grounded: {len(log.named_actor_profiles)}")
    lines.append("")
    for actor in log.named_actor_profiles[:6]:
        priorities = ", ".join(actor.get("current_priorities", [])[:3]) or "n/a"
        constraints = ", ".join(actor.get("constraints", [])[:2]) or "n/a"
        lines.append(
            f"- {actor.get('country')}: {actor.get('name')}, {actor.get('title')} | "
            f"style `{actor.get('typical_response_style', 'n/a')}` | priorities `{priorities}` | "
            f"constraints `{constraints}` | confidence `{actor.get('confidence', 'medium')}`"
        )

    if log.leadership_grounding_summary:
        lines.append("")
        lines.append("### Grounding Notes")
        lines.append("")
        for raw_line in log.leadership_grounding_summary.splitlines():
            if raw_line.startswith("- "):
                lines.append(raw_line)

    return "\n".join(lines)


def _country_risk_scores(
    agents: list[AgentProfile],
    ws: WorldState,
) -> list[tuple[str, float, float, float, float]]:
    latest = ws.history[-1] if ws.history else None
    if not latest:
        return []

    countries = sorted({agent.country for agent in agents})
    distress_by_country: dict[str, float] = {}
    for country in countries:
        country_agents = [agent for agent in agents if agent.country == country]
        if not country_agents:
            continue
        distress_by_country[country] = sum(
            1 for agent in country_agents if agent.emotional_state in DISTRESS_STATES
        ) / len(country_agents)

    volatility_map = _country_volatility(ws)
    results = []
    for country in countries:
        stress = latest.economic_stress.get(country, 0.0)
        distress = distress_by_country.get(country, 0.0)
        volatility = volatility_map.get(country, 0.0)
        risk_score = 0.5 * stress + 0.3 * distress + 0.2 * volatility
        results.append((country, risk_score, stress, distress, volatility))

    return sorted(results, key=lambda item: item[1], reverse=True)


def _segment_volatility(ws: WorldState) -> list[tuple[str, float, float]]:
    series: dict[str, list[float]] = defaultdict(list)
    for snapshot in ws.history:
        for segment, value in snapshot.economic_stress.items():
            series[segment].append(value)

    scored = []
    for segment, values in series.items():
        if len(values) < 2:
            continue
        amplitude = max(values) - min(values)
        scored.append((segment, amplitude, values[-1]))
    return sorted(scored, key=lambda item: item[1], reverse=True)


def _country_volatility(ws: WorldState) -> dict[str, float]:
    return {
        segment: amplitude
        for segment, amplitude, _latest in _segment_volatility(ws)
        if not segment.startswith("income_") and not segment.startswith("ideology_")
    }


def _amplifier_nodes(log: SimulationLog, agents: list[AgentProfile]) -> list[str]:
    id_map = {agent.id: agent for agent in agents}
    source_scores: dict[str, float] = defaultdict(float)
    source_edges: Counter[str] = Counter()
    bridge_countries: dict[str, set[str]] = defaultdict(set)

    for cascade in log.cascades:
        for edge in cascade.edges:
            source_scores[edge.source_id] += edge.weight
            source_edges[edge.source_id] += 1
            source_country = id_map.get(edge.source_id).country if edge.source_id in id_map else None
            target_country = id_map.get(edge.target_id).country if edge.target_id in id_map else None
            if source_country and target_country and source_country != target_country:
                bridge_countries[edge.source_id].add(target_country)

    scored = []
    for agent_id, score in source_scores.items():
        agent = id_map.get(agent_id)
        if not agent:
            continue
        scored.append(
            (
                agent_id,
                score + len(bridge_countries.get(agent_id, set())) * 0.5,
                f"{agent.name} ({agent.country}): relay score `{score:.2f}`, "
                f"activated `{source_edges[agent_id]}` edges, "
                f"crossed into `{len(bridge_countries.get(agent_id, set()))}` other country clusters",
            )
        )
    scored.sort(key=lambda item: item[1], reverse=True)
    return [item[2] for item in scored]


def _absorber_countries(log: SimulationLog, agents: list[AgentProfile]) -> list[str]:
    id_map = {agent.id: agent for agent in agents}
    incoming: Counter[str] = Counter()
    outgoing: Counter[str] = Counter()

    for cascade in log.cascades:
        for edge in cascade.edges:
            source = id_map.get(edge.source_id)
            target = id_map.get(edge.target_id)
            if not source or not target:
                continue
            outgoing[source.country] += 1
            incoming[target.country] += 1

    scored = []
    for country in sorted({agent.country for agent in agents}):
        intake = incoming[country]
        relay = outgoing[country]
        if intake == 0 and relay == 0:
            continue
        absorption = intake - relay
        if absorption > 0:
            scored.append(
                (
                    absorption,
                    f"{country}: absorbed `{intake}` incoming relays and retransmitted `{relay}`, suggesting pressure accumulated locally faster than it spread outward.",
                )
            )
    scored.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in scored]


def _leading_indicators(log: SimulationLog, agents: list[AgentProfile], ws: WorldState) -> list[str]:
    indicators: list[str] = []
    if not ws.history:
        return indicators

    first = ws.history[0]
    latest = ws.history[-1]
    polarization_change = latest.political_polarization - first.political_polarization
    stress_change = _avg_stress(latest) - _avg_stress(first)
    if polarization_change > 0.08:
        indicators.append(
            f"Polarization rose by `{polarization_change:+.2f}` from week 1 to week {latest.step}, a clear precursor to institutional strain."
        )
    if stress_change > 0.08:
        indicators.append(
            f"Average economic stress rose by `{stress_change:+.2f}`, indicating households were not absorbing the shock cleanly."
        )

    distress_share = _distress_share(agents)
    if distress_share >= 0.45:
        indicators.append(
            f"Distress states reached `{distress_share * 100:.0f}%` of archetypes, which raises the chance that sentiment shocks convert into broader instability."
        )

    volatile_segments = _segment_volatility(ws)
    if volatile_segments:
        segment, amplitude, latest_value = volatile_segments[0]
        indicators.append(
            f"The most unstable segment was `{segment}` with stress amplitude `{amplitude:.2f}` and latest stress `{latest_value:.2f}`."
        )

    if log.emergent_events:
        earliest = min(log.emergent_events, key=lambda event: event.step_introduced)
        indicators.append(
            f"The first emergent event appeared in week `{earliest.step_introduced}`, showing rapid conversion from micro-reactions to macro behavior."
        )

    return indicators[:5]


def _dominant_emotions(agents: list[AgentProfile]) -> str:
    counts = Counter(agent.emotional_state for agent in agents)
    return ", ".join(
        f"{emotion}={count}" for emotion, count in counts.most_common(4)
    ) or "n/a"


def _distress_share(agents: list[AgentProfile]) -> float:
    if not agents:
        return 0.0
    distressed = sum(1 for agent in agents if agent.emotional_state in DISTRESS_STATES)
    return distressed / len(agents)


def _avg_stress(snapshot: StepSnapshot | None) -> float:
    if not snapshot or not snapshot.economic_stress:
        return 0.0
    return sum(snapshot.economic_stress.values()) / len(snapshot.economic_stress)


def _assemble_markdown(log: SimulationLog, sections: dict[str, str]) -> str:
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return "\n\n".join([
        f"# The Small World Decision Brief\n\nGenerated: {generated_at}",
        f"Scenario class: **{log.scenario_classification or 'strategic shock'}**  \nDecision lens: **{log.decision_lens or 'general'}**",
        sections["executive"],
        sections["baseline"],
        sections["leadership"],
        sections["stress_map"],
        sections["propagation"],
        sections["indicators"],
        sections["signals"],
        sections["appendix"],
    ]).strip() + "\n"
