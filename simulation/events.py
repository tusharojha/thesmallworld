import json
import os
from dataclasses import dataclass, field
from openai import AsyncOpenAI


@dataclass
class MediaFraming:
    source_type: str    # e.g. "state_media", "cable_news_right", "social_media"
    headline: str       # how this source frames the event
    sentiment: float    # -1.0 (hostile) to 1.0 (positive)


@dataclass
class InitialEvent:
    topic: str
    description: str                          # neutral description of the event
    geographic_reach: list[str]               # countries / regions initially reached
    media_framings: list[MediaFraming]        # how different media channels frame it
    economic_impact_signal: str               # e.g. "major positive", "minor negative", "unclear"
    political_salience: float                 # 0.0–1.0 how politically charged
    step_introduced: int = 0                  # which simulation step this fires


@dataclass
class EmergentEvent:
    topic: str
    description: str
    triggered_by: str                         # which prior event or agent group drove this
    geographic_reach: list[str]
    step_introduced: int


def _llm_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )


def _model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o")


async def inject_theory(theory: str, grounding_context: str = "") -> list[InitialEvent]:
    """Parse free-text theory into structured InitialEvents via LLM."""
    client = _llm_client()

    system_prompt = """You are a world-simulation event designer. Given a "what-if" theory,
produce a JSON array of 3-6 initial events that would occur in the first few weeks after this theory becomes reality.

Each event should be a JSON object with:
- topic: short label (e.g. "UBI_announcement", "economic_uncertainty")
- description: neutral 1-2 sentence description of what happened
- geographic_reach: list of regions (use: "USA", "Europe", "India", "Brazil", "Nigeria", "China",
  "Middle East", "Southeast Asia", "Latin America", "Sub-Saharan Africa", "Russia", "Japan/Korea",
  "Scandinavia", "global")
- media_framings: array of objects with source_type, headline, sentiment (-1.0 to 1.0).
  Cover at least: "cable_news_right", "online_liberal_media", "state_media", "social_media",
  "local_radio", "financial_press", "public_broadcaster", "word_of_mouth"
- economic_impact_signal: one of "major positive", "moderate positive", "minor positive",
  "unclear", "minor negative", "moderate negative", "major negative"
- political_salience: float 0.0-1.0

Return ONLY a valid JSON array. No prose."""

    response = await client.chat.completions.create(
        model=_model(),
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Theory: {theory}\n\n"
                    f"Current grounding context:\n{grounding_context or 'No extra grounding provided.'}"
                ),
            },
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    # The model returns {"events": [...]} or just [...]
    parsed = json.loads(raw)
    events_data = parsed.get("events", parsed) if isinstance(parsed, dict) else parsed

    events = []
    for e in events_data:
        framings = [
            MediaFraming(
                source_type=f["source_type"],
                headline=f["headline"],
                sentiment=float(f["sentiment"]),
            )
            for f in e.get("media_framings", [])
        ]
        events.append(InitialEvent(
            topic=e["topic"],
            description=e["description"],
            geographic_reach=e.get("geographic_reach", ["global"]),
            media_framings=framings,
            economic_impact_signal=e.get("economic_impact_signal", "unclear"),
            political_salience=float(e.get("political_salience", 0.5)),
        ))

    return events


def get_framing_for_agent(event: InitialEvent, agent_media_sources: list[str]) -> str:
    """Return the most relevant headline framing for an agent given their media diet."""
    for source in agent_media_sources:
        for framing in event.media_framings:
            if framing.source_type == source:
                return framing.headline

    # Fall back to first available framing
    if event.media_framings:
        return event.media_framings[0].headline

    return event.description


def agent_receives_event(event: InitialEvent | EmergentEvent, agent_country: str) -> bool:
    """Determine if an agent's country receives this event."""
    reach = event.geographic_reach
    if "global" in reach:
        return True

    country_to_region = {
        "USA": ["USA", "global"],
        "Canada": ["Canada", "global"],
        "Australia": ["Australia", "global"],
        "UK": ["Europe", "global"],
        "Germany": ["Europe", "global"],
        "France": ["Europe", "global"],
        "Poland": ["Europe", "global"],
        "Sweden": ["Scandinavia", "global"],
        "Norway": ["Scandinavia", "global"],
        "Russia": ["Russia", "global"],
        "India": ["India", "global"],
        "China": ["China", "global"],
        "Japan": ["Japan/Korea", "global"],
        "South Korea": ["Japan/Korea", "global"],
        "Nigeria": ["Nigeria", "Sub-Saharan Africa", "global"],
        "Ghana": ["Sub-Saharan Africa", "global"],
        "Ethiopia": ["Sub-Saharan Africa", "global"],
        "Brazil": ["Brazil", "Latin America", "global"],
        "Mexico": ["Latin America", "global"],
        "Colombia": ["Latin America", "global"],
        "Egypt": ["Middle East", "global"],
        "Saudi Arabia": ["Middle East", "global"],
        "Thailand": ["Southeast Asia", "global"],
        "Indonesia": ["Southeast Asia", "global"],
    }

    agent_regions = country_to_region.get(agent_country, [agent_country])
    return any(r in reach for r in agent_regions)
