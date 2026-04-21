import asyncio
import json
import os
import random
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass

import networkx as nx
from openai import AsyncOpenAI

from agents.profile import AgentProfile
from simulation.events import (
    InitialEvent, EmergentEvent,
    agent_receives_event, get_framing_for_agent,
)
from simulation.world_state import WorldState


@dataclass
class Conversation:
    step: int
    agent_a: str
    agent_b: str
    topic: str
    exchange: str


@dataclass
class CascadeEdge:
    source_id: str
    target_id: str
    hop: int
    weight: float
    topic: str
    message: str


@dataclass
class CascadeTrace:
    step: int
    topic: str
    origin_label: str
    origin_agent_id: str | None
    direct_recipients: list[str]
    influenced_agents: list[str]
    edges: list[CascadeEdge]


@dataclass
class SocialRipple:
    step_introduced: int
    source_agent_id: str
    topic: str
    message: str
    intensity: float = 1.0


@dataclass
class SimulationLog:
    theory: str
    steps_run: int
    conversations: list[Conversation]
    emergent_events: list[EmergentEvent]
    cascades: list[CascadeTrace]
    world_state: WorldState
    current_world_state_summary: str = ""


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )


def _model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


_AGENT_SYSTEM = """You are simulating a real person. Stay fully in character.
Respond in JSON with exactly these keys:
- reaction: 1-2 sentence emotional/cognitive reaction to the events
- belief_updates: object mapping at most 3 snake_case topics to sentiment float (-1.0 hostile to 1.0 supportive)
- emotional_state: one of neutral/hopeful/anxious/angry/fearful/excited/resigned/determined
- decisions: list of 0-3 short action strings (things you decide to do)
- step_summary: 1 sentence summarizing your week
Do not make the character artificially balanced, polite, or accepting. Let them be self-protective,
skeptical, tribal, avoidant, cynical, or conflicted when that fits their profile. Reuse existing
topic labels when possible and avoid near-duplicate topic names."""

_CONVO_SYSTEM = """Simulate a realistic conversation between two people with the given profiles.
Format as a short dialogue (4-8 exchanges), attributed by first name.
Keep it authentic to their background, ideology, and emotional state.
Return a single formatted string — no JSON."""

_EMERGENT_SYSTEM = """You are analyzing a social simulation. Given agent reactions and world state,
identify 1-3 emergent societal events that would plausibly follow in the next week.
Return JSON with key "events" containing an array of objects with:
topic, description, triggered_by, geographic_reach (array of regions).
Only return events that genuinely emerge from the data — not obvious repetitions."""


async def _process_agent(
    client: AsyncOpenAI,
    agent: AgentProfile,
    incoming_events: list[str],
    semaphore: asyncio.Semaphore,
    step: int,
) -> dict:
    if not incoming_events:
        return {
            "id": agent.id,
            "reaction": "Nothing significant reached me this week.",
            "belief_updates": {},
            "emotional_state": agent.emotional_state,
            "decisions": [],
            "step_summary": "A quiet week with no major news.",
        }

    events_text = "\n".join(f"- {e}" for e in incoming_events)
    user_msg = (
        f"Your profile: {agent.short_bio()}\n"
        f"{agent.personality_summary()}\n"
        f"Current emotional state: {agent.emotional_state}\n"
        f"{agent.memory_context()}\n\n"
        f"Events that reached you this week:\n{events_text}\n\n"
        f"How do you react?"
    )

    async with semaphore:
        resp = await client.chat.completions.create(
            model=_model(),
            messages=[
                {"role": "system", "content": _AGENT_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.8,
            response_format={"type": "json_object"},
        )

    result = json.loads(resp.choices[0].message.content)
    result["id"] = agent.id
    return result


async def _process_agent_tracked(
    client: AsyncOpenAI,
    agent: AgentProfile,
    incoming_events: list[str],
    semaphore: asyncio.Semaphore,
    step: int,
    on_start: Callable | None,
    on_complete: Callable | None,
) -> dict:
    if on_start:
        on_start(agent.id)
    result = await _process_agent(client, agent, incoming_events, semaphore, step)
    if on_complete:
        on_complete(agent.id, result.get("emotional_state", "neutral"), result.get("reaction", ""))
    return result


async def _generate_conversation(
    client: AsyncOpenAI,
    agent_a: AgentProfile,
    agent_b: AgentProfile,
    topic: str,
    semaphore: asyncio.Semaphore,
    step: int,
    on_chunk: Callable | None = None,
) -> Conversation:
    user_msg = (
        f"Person A: {agent_a.short_bio()} Emotional state: {agent_a.emotional_state}\n"
        f"Person B: {agent_b.short_bio()} Emotional state: {agent_b.emotional_state}\n\n"
        f"They discuss: {topic}"
    )

    full_text = ""
    async with semaphore:
        stream = await client.chat.completions.create(
            model=_model(),
            messages=[
                {"role": "system", "content": _CONVO_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.9,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                full_text += delta
                if on_chunk:
                    on_chunk(delta)

    return Conversation(
        step=step,
        agent_a=agent_a.name,
        agent_b=agent_b.name,
        topic=topic,
        exchange=full_text.strip(),
    )


async def _generate_emergent_events(
    client: AsyncOpenAI,
    reactions_summary: str,
    world_state: WorldState,
    step: int,
    semaphore: asyncio.Semaphore,
) -> list[EmergentEvent]:
    snap = world_state.history[-1] if world_state.history else None
    context = reactions_summary
    if snap:
        context += f"\nPolarization: {snap.political_polarization:.2f}"

    async with semaphore:
        resp = await client.chat.completions.create(
            model=_model(),
            messages=[
                {"role": "system", "content": _EMERGENT_SYSTEM},
                {"role": "user", "content": context},
            ],
            temperature=0.75,
            response_format={"type": "json_object"},
        )

    raw = json.loads(resp.choices[0].message.content)
    events_data = raw.get("events", [])
    if isinstance(events_data, dict):
        events_data = [events_data]

    return [
        EmergentEvent(
            topic=e.get("topic", "unknown"),
            description=e.get("description", ""),
            triggered_by=e.get("triggered_by", "agent reactions"),
            geographic_reach=e.get("geographic_reach", ["global"]),
            step_introduced=step,
        )
        for e in events_data
    ]


async def run_simulation(
    theory: str,
    agents: list[AgentProfile],
    social_graph: nx.Graph,
    initial_events: list[InitialEvent],
    n_steps: int,
    on_agent_start: Callable[[str], None] | None = None,
    on_agent_complete: Callable[[str, str, str], None] | None = None,
    on_conversation_chunk: Callable[[str, str, str, str], None] | None = None,
    on_emergent_event: Callable | None = None,
    on_step_start: Callable[[int], None] | None = None,
    on_step_complete: Callable | None = None,
    concurrency: int = 20,
) -> SimulationLog:
    client = _client()
    semaphore = asyncio.Semaphore(concurrency)
    world_state = WorldState(agents)
    all_conversations: list[Conversation] = []
    all_emergent: list[EmergentEvent] = []
    all_cascades: list[CascadeTrace] = []
    active_events: list[InitialEvent | EmergentEvent] = list(initial_events)
    active_ripples: list[SocialRipple] = []
    id_map = {a.id: a for a in agents}

    for step in range(1, n_steps + 1):
        if on_step_start:
            on_step_start(step)

        # ── 1. Build agent inboxes ────────────────────────────────────────────
        agent_inboxes: dict[str, list[str]] = {a.id: [] for a in agents}
        step_cascades: list[CascadeTrace] = []

        for event in active_events:
            if isinstance(event, InitialEvent) and event.step_introduced > step:
                continue
            if isinstance(event, EmergentEvent) and event.step_introduced >= step:
                continue
            direct_messages: dict[str, str] = {}
            for agent in agents:
                if not agent_receives_event(event, agent.country):
                    continue
                if isinstance(event, InitialEvent):
                    direct_messages[agent.id] = get_framing_for_agent(event, agent.media_sources)
                else:
                    direct_messages[agent.id] = event.description

            cascade = _propagate_cascade(
                step=step,
                topic=event.topic,
                origin_label=event.topic,
                direct_messages=direct_messages,
                graph=social_graph,
                agents=agents,
            )
            _apply_cascade_to_inboxes(cascade, agent_inboxes, id_map)
            step_cascades.append(cascade)

        retained_ripples: list[SocialRipple] = []
        for ripple in active_ripples:
            if ripple.step_introduced >= step:
                retained_ripples.append(ripple)
                continue

            source_agent = id_map.get(ripple.source_agent_id)
            if not source_agent:
                continue

            direct_messages = {source_agent.id: ripple.message}
            cascade = _propagate_cascade(
                step=step,
                topic=ripple.topic,
                origin_label=source_agent.name,
                direct_messages=direct_messages,
                graph=social_graph,
                agents=agents,
                max_hops=3,
                decay=0.72,
            )
            _apply_cascade_to_inboxes(cascade, agent_inboxes, id_map)
            step_cascades.append(cascade)
            if step - ripple.step_introduced < 2:
                retained_ripples.append(ripple)
        active_ripples = retained_ripples

        # ── 2. Process all agents in parallel ─────────────────────────────────
        tasks = [
            _process_agent_tracked(
                client, agent, agent_inboxes[agent.id], semaphore, step,
                on_agent_start, on_agent_complete,
            )
            for agent in agents
        ]
        results = await asyncio.gather(*tasks)
        result_map = {r["id"]: r for r in results}

        for r in results:
            world_state.update_agent(
                agent_id=r["id"],
                beliefs=r.get("belief_updates", {}),
                emotional_state=r.get("emotional_state", "neutral"),
                decisions=r.get("decisions", []),
                step_summary=r.get("step_summary", ""),
                step=step,
            )

        # ── 3. Social ripples for next step ───────────────────────────────────
        new_ripples = _build_social_ripples(results, agents, step)
        active_ripples.extend(new_ripples)

        # ── 4. Conversations (streamed) ────────────────────────────────────────
        conversation_pairs = _select_conversation_pairs(agents, social_graph, step_cascades, result_map, n=5)
        hot_topics = _extract_hot_topics(results)
        primary_topic = hot_topics[0] if hot_topics else theory

        def _make_chunk_cb(a_name: str, b_name: str, topic: str) -> Callable | None:
            if not on_conversation_chunk:
                return None
            def cb(chunk: str):
                on_conversation_chunk(a_name, b_name, topic, chunk)
            return cb

        conv_tasks = [
            _generate_conversation(
                client, a, b, primary_topic, semaphore, step,
                on_chunk=_make_chunk_cb(a.name, b.name, primary_topic),
            )
            for a, b in conversation_pairs
        ]
        step_conversations = await asyncio.gather(*conv_tasks)
        all_conversations.extend(step_conversations)

        # ── 5. Emergent events ────────────────────────────────────────────────
        reactions_summary = _summarize_reactions(results, agents, step_cascades)
        emergent = await _generate_emergent_events(client, reactions_summary, world_state, step, semaphore)
        for e in emergent:
            if on_emergent_event:
                on_emergent_event(e)
        all_emergent.extend(emergent)
        active_events.extend(emergent)
        all_cascades.extend(step_cascades)

        # ── 6. Snapshot ───────────────────────────────────────────────────────
        notable = [e.description[:80] for e in emergent]
        cascade_summaries = [_cascade_summary(c) for c in step_cascades[:6]]
        snapshot = world_state.snapshot(step, notable, cascade_summaries)

        if on_step_complete:
            on_step_complete(step, snapshot, list(step_conversations))

    return SimulationLog(
        theory=theory,
        steps_run=n_steps,
        conversations=all_conversations,
        emergent_events=all_emergent,
        cascades=all_cascades,
        world_state=world_state,
    )


def _select_conversation_pairs(
    agents: list[AgentProfile],
    graph: nx.Graph,
    cascades: list[CascadeTrace],
    result_map: dict[str, dict],
    n: int,
) -> list[tuple[AgentProfile, AgentProfile]]:
    id_map = {a.id: a for a in agents}
    if not graph.edges():
        return []

    edge_scores: dict[tuple[str, str], float] = defaultdict(float)
    for cascade in cascades:
        for edge in cascade.edges:
            key = tuple(sorted((edge.source_id, edge.target_id)))
            edge_scores[key] += edge.weight / max(1, edge.hop)

    if not edge_scores:
        for a, b in graph.edges():
            key = tuple(sorted((a, b)))
            edge_scores[key] = graph[a][b].get("weight", 0.5)

    def score(edge_key: tuple[str, str]) -> float:
        a, b = edge_key
        ideology_gap = abs(id_map[a].political_ideology - id_map[b].political_ideology)
        reaction_energy = (
            _result_energy(result_map.get(a, {})) + _result_energy(result_map.get(b, {}))
        )
        return edge_scores[edge_key] + ideology_gap + reaction_energy

    selected = sorted(edge_scores, key=score, reverse=True)[:n]
    return [(id_map[a], id_map[b]) for a, b in selected if a in id_map and b in id_map]


def _extract_hot_topics(results: list[dict]) -> list[str]:
    topic_counts: dict[str, int] = {}
    for r in results:
        for topic in r.get("belief_updates", {}).keys():
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
    return sorted(topic_counts, key=lambda t: -topic_counts[t])


def _summarize_reactions(results: list[dict], agents: list[AgentProfile], cascades: list[CascadeTrace]) -> str:
    id_map = {a.id: a for a in agents}
    lines = []
    for r in results:
        agent = id_map.get(r["id"])
        if not agent:
            continue
        lines.append(
            f"- {agent.name} ({agent.country}, ideology {agent.political_ideology:.1f}, "
            f"{agent.income_bracket} income): {r.get('reaction', '')} "
            f"State: {r.get('emotional_state', 'neutral')}. "
            f"Decisions: {', '.join(r.get('decisions', [])) or 'none'}."
        )
    if cascades:
        lines.append("Cascade traces:")
        for cascade in cascades[:8]:
            lines.append(f"- {_cascade_summary(cascade)}")
    return "\n".join(lines)


def _propagate_cascade(
    step: int,
    topic: str,
    origin_label: str,
    direct_messages: dict[str, str],
    graph: nx.Graph,
    agents: list[AgentProfile],
    max_hops: int = 2,
    decay: float = 0.68,
) -> CascadeTrace:
    id_map = {a.id: a for a in agents}
    direct_recipients = list(direct_messages)
    influenced_agents = set(direct_messages)
    edges: list[CascadeEdge] = []
    frontier = [(agent_id, direct_messages[agent_id], 1.0) for agent_id in direct_recipients]
    rng = random.Random(f"{step}:{topic}:{origin_label}")

    for hop in range(1, max_hops + 1):
        next_frontier: list[tuple[str, str, float]] = []
        for source_id, message, carried_intensity in frontier:
            if source_id not in graph:
                continue
            source_agent = id_map.get(source_id)
            if not source_agent:
                continue
            neighbors = list(graph.neighbors(source_id))
            neighbors.sort(key=lambda nid: graph[source_id][nid].get("weight", 0.0), reverse=True)
            for target_id in neighbors[:4]:
                if target_id in influenced_agents:
                    continue
                edge_weight = float(graph[source_id][target_id].get("weight", 0.5))
                source_push = 0.55 + source_agent.extraversion * 0.25
                influence_score = carried_intensity * edge_weight * source_push * (decay ** (hop - 1))
                threshold = 0.28 + rng.random() * 0.14
                if influence_score < threshold:
                    continue
                target_agent = id_map.get(target_id)
                if not target_agent:
                    continue
                relayed = (
                    f"Network relay from {source_agent.name} to {target_agent.name} about {topic}: "
                    f"{message[:140]}"
                )
                edges.append(
                    CascadeEdge(
                        source_id=source_id,
                        target_id=target_id,
                        hop=hop,
                        weight=round(influence_score, 3),
                        topic=topic,
                        message=relayed,
                    )
                )
                influenced_agents.add(target_id)
                next_frontier.append((target_id, relayed, influence_score))
        frontier = next_frontier
        if not frontier:
            break

    return CascadeTrace(
        step=step,
        topic=topic,
        origin_label=origin_label,
        origin_agent_id=direct_recipients[0] if len(direct_recipients) == 1 else None,
        direct_recipients=direct_recipients,
        influenced_agents=sorted(influenced_agents),
        edges=edges,
    )


def _apply_cascade_to_inboxes(
    cascade: CascadeTrace,
    agent_inboxes: dict[str, list[str]],
    id_map: dict[str, AgentProfile],
) -> None:
    for agent_id in cascade.direct_recipients:
        if agent_id in agent_inboxes and agent_id in id_map:
            agent_inboxes[agent_id].append(
                f"Direct exposure on {cascade.topic}: {cascade.topic.replace('_', ' ')}"
            )
    for edge in cascade.edges:
        if edge.target_id not in agent_inboxes:
            continue
        source_name = id_map[edge.source_id].name if edge.source_id in id_map else edge.source_id
        agent_inboxes[edge.target_id].append(
            f"Through your network, {source_name} relayed this on {cascade.topic}: {edge.message}"
        )


def _build_social_ripples(results: list[dict], agents: list[AgentProfile], step: int) -> list[SocialRipple]:
    id_map = {a.id: a for a in agents}
    scored = sorted(
        results,
        key=lambda r: _result_energy(r),
        reverse=True,
    )
    ripples: list[SocialRipple] = []
    for result in scored[:6]:
        if _result_energy(result) < 0.35:
            continue
        agent = id_map.get(result["id"])
        if not agent:
            continue
        topic = next(iter(result.get("belief_updates", {}) or {"social_reaction": 0.0}))
        message = result.get("step_summary") or result.get("reaction") or "Strong reaction to unfolding events."
        ripples.append(
            SocialRipple(
                step_introduced=step,
                source_agent_id=agent.id,
                topic=topic,
                message=message,
                intensity=min(1.0, _result_energy(result)),
            )
        )
    return ripples


def _result_energy(result: dict) -> float:
    belief_energy = sum(abs(v) for v in result.get("belief_updates", {}).values())
    decision_energy = len(result.get("decisions", [])) * 0.2
    reaction_bonus = 0.15 if result.get("reaction") else 0.0
    return min(1.5, belief_energy + decision_energy + reaction_bonus)


def _cascade_summary(cascade: CascadeTrace) -> str:
    return (
        f"{cascade.origin_label} on {cascade.topic}: "
        f"{len(cascade.direct_recipients)} direct, "
        f"{max(0, len(cascade.influenced_agents) - len(cascade.direct_recipients))} relayed, "
        f"{len(cascade.edges)} network edges activated"
    )
