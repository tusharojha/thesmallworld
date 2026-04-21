import json
import os
from datetime import datetime
from pathlib import Path

from openai import AsyncOpenAI

from simulation.engine import SimulationLog


def build_artifact(
    log: SimulationLog,
    report_md: str,
    artifact_version: str = "1",
) -> dict[str, object]:
    agents = []
    for agent in log.world_state.agents.values():
        agents.append({
            "id": agent.id,
            "name": agent.name,
            "country": agent.country,
            "occupation": agent.occupation,
            "emotion": agent.emotional_state,
            "beliefs": agent.current_beliefs,
            "decisions": agent.decisions[-5:],
            "memory": agent.memory[-5:],
            "connections": len(agent.social_connections),
        })

    return {
        "artifact_version": artifact_version,
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "theory": log.theory,
        "scenario_classification": log.scenario_classification,
        "decision_lens": log.decision_lens,
        "baseline_confidence": log.baseline_confidence,
        "current_world_state_summary": log.current_world_state_summary,
        "leadership_grounding_summary": log.leadership_grounding_summary,
        "named_actor_profiles": log.named_actor_profiles,
        "report_markdown": report_md,
        "emergent_events": [
            {
                "topic": event.topic,
                "description": event.description,
                "triggered_by": event.triggered_by,
                "geographic_reach": event.geographic_reach,
                "step_introduced": event.step_introduced,
            }
            for event in log.emergent_events
        ],
        "cascades": [
            {
                "step": cascade.step,
                "topic": cascade.topic,
                "origin_label": cascade.origin_label,
                "direct_recipients": cascade.direct_recipients,
                "influenced_agents": cascade.influenced_agents,
                "edge_count": len(cascade.edges),
            }
            for cascade in log.cascades
        ],
        "conversations": [
            {
                "step": convo.step,
                "agent_a": convo.agent_a,
                "agent_b": convo.agent_b,
                "topic": convo.topic,
                "exchange": convo.exchange,
            }
            for convo in log.conversations
        ],
        "agents": agents,
    }


def save_artifact(path: str, artifact: dict[str, object]) -> None:
    Path(path).write_text(json.dumps(artifact, indent=2, ensure_ascii=True), encoding="utf-8")


def load_artifact(path: str) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def artifact_excerpt(artifact: dict[str, object], max_conversations: int = 4, max_agents: int = 8) -> str:
    lines = [
        f"Theory: {artifact.get('theory', '')}",
        f"Scenario class: {artifact.get('scenario_classification', '')}",
        f"Decision lens: {artifact.get('decision_lens', '')}",
        f"Baseline confidence: {artifact.get('baseline_confidence', '')}",
        "",
        "Current world state summary:",
        str(artifact.get("current_world_state_summary", ""))[:2500],
        "",
        "Leadership grounding summary:",
        str(artifact.get("leadership_grounding_summary", ""))[:2000],
        "",
        "Representative agents:",
    ]
    for agent in artifact.get("agents", [])[:max_agents]:
        lines.append(
            f"- {agent.get('name')} ({agent.get('country')}, {agent.get('occupation')}): "
            f"emotion={agent.get('emotion')}, decisions={', '.join(agent.get('decisions', [])[:3]) or 'none'}"
        )
    lines.append("")
    lines.append("Representative conversations:")
    for convo in artifact.get("conversations", [])[:max_conversations]:
        lines.append(
            f"- Week {convo.get('step')}: {convo.get('agent_a')} x {convo.get('agent_b')} on {convo.get('topic')}"
        )
        lines.append(f"  {str(convo.get('exchange', ''))[:700]}")
    lines.append("")
    lines.append("Report:")
    lines.append(str(artifact.get("report_markdown", ""))[:5000])
    return "\n".join(lines)


def search_artifact(artifact: dict[str, object], query: str) -> list[str]:
    needle = query.lower()
    matches: list[str] = []

    for event in artifact.get("emergent_events", []):
        line = f"event {event.get('topic')}: {event.get('description')}"
        if needle in line.lower():
            matches.append(line)

    for convo in artifact.get("conversations", []):
        line = f"conversation {convo.get('agent_a')} x {convo.get('agent_b')} on {convo.get('topic')}: {str(convo.get('exchange', ''))[:300]}"
        if needle in line.lower():
            matches.append(line)

    for agent in artifact.get("agents", []):
        line = f"agent {agent.get('name')} ({agent.get('country')}, {agent.get('occupation')}): emotion={agent.get('emotion')}, beliefs={agent.get('beliefs')}"
        if needle in line.lower():
            matches.append(line)

    report_text = str(artifact.get("report_markdown", ""))
    for paragraph in report_text.split("\n\n"):
        if needle in paragraph.lower():
            matches.append(paragraph[:500])

    return matches[:12]


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )


async def ask_artifact(artifact: dict[str, object], question: str) -> str:
    if not os.environ.get("OPENAI_API_KEY"):
        matches = search_artifact(artifact, question)
        if not matches:
            return "No matching passages were found in the saved world artifact."
        return "Offline artifact search results:\n- " + "\n- ".join(matches[:6])

    response = await _client().chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer questions about a simulated world artifact. "
                    "Be explicit about what comes from the saved world state, conversations, and report. "
                    "Do not invent details that are absent from the artifact."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Artifact excerpt:\n{artifact_excerpt(artifact)}"
                ),
            },
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or "No answer returned."
