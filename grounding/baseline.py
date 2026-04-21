import asyncio
import json
import os
from dataclasses import dataclass, field

from openai import AsyncOpenAI

from agents.profile import AgentProfile
from grounding.live_data import CountryStats, fetch_country_stats
from grounding.search import SearchProvider, build_search_provider


@dataclass
class WorldStateOptions:
    mode: str = "static"
    search_provider: str = "none"
    searxng_base_url: str | None = None
    brave_api_key: str | None = None


@dataclass
class TopicPulse:
    topic_key: str
    left_sentiment: float = 0.0
    center_sentiment: float = 0.0
    right_sentiment: float = 0.0
    country_sentiments: dict[str, float] = field(default_factory=dict)
    key_narratives: list[str] = field(default_factory=list)
    economic_channels: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)


@dataclass
class CurrentWorldState:
    theory: str
    country_stats: dict[str, CountryStats]
    topic_pulse: TopicPulse | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class BaselineAssessment:
    scenario_classification: str
    observed_signal_count: int
    inferred_signal_count: int
    country_coverage_ratio: float
    baseline_confidence: str
    source_count: int
    observed_state: list[str] = field(default_factory=list)
    inferred_state: list[str] = field(default_factory=list)


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )


def _model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def _slugify_topic(theory: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in theory)
    return "_".join(part for part in cleaned.split("_") if part)[:48] or "theory_topic"


async def _build_topic_pulse(
    theory: str,
    countries: list[str],
    provider: SearchProvider,
) -> TopicPulse | None:
    queries = [
        f"{theory} left right center public debate",
        f"{theory} supporters critics polling economic impact",
        f"{theory} reaction {', '.join(countries[:4])}",
    ]

    gathered_results = []
    for query in queries:
        for result in provider.search(query, count=5):
            gathered_results.append(result)

    if not gathered_results:
        return None

    snippets = "\n".join(
        f"- {r.title}\n  URL: {r.url}\n  Snippet: {r.snippet}"
        for r in gathered_results[:12]
    )

    client = _client()
    response = await client.chat.completions.create(
        model=_model(),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are grounding a simulation with current public discourse. "
                    "Return JSON with keys: topic_key, left_sentiment, center_sentiment, "
                    "right_sentiment, country_sentiments, key_narratives, economic_channels. "
                    "Sentiment values must be floats from -1.0 to 1.0."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Theory: {theory}\n"
                    f"Countries represented: {', '.join(countries)}\n\n"
                    f"Current search snippets:\n{snippets}"
                ),
            },
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    raw = json.loads(response.choices[0].message.content)
    return TopicPulse(
        topic_key=raw.get("topic_key") or _slugify_topic(theory),
        left_sentiment=float(raw.get("left_sentiment", 0.0)),
        center_sentiment=float(raw.get("center_sentiment", 0.0)),
        right_sentiment=float(raw.get("right_sentiment", 0.0)),
        country_sentiments={
            str(k): float(v) for k, v in raw.get("country_sentiments", {}).items()
        },
        key_narratives=[str(x) for x in raw.get("key_narratives", [])[:6]],
        economic_channels=[str(x) for x in raw.get("economic_channels", [])[:6]],
        source_urls=[r.url for r in gathered_results[:12]],
    )


async def build_current_world_state(
    theory: str,
    countries: list[str],
    options: WorldStateOptions,
) -> CurrentWorldState:
    if options.mode != "live":
        return CurrentWorldState(
            theory=theory,
            country_stats={},
            notes=["Static world-state mode selected; live reconstruction skipped."],
        )

    stats = await asyncio.to_thread(fetch_country_stats, countries)
    provider = build_search_provider(
        options.search_provider,
        brave_api_key=options.brave_api_key,
        searxng_base_url=options.searxng_base_url,
    )

    topic_pulse: TopicPulse | None = None
    notes = ["Loaded latest available country indicators from the World Bank API."]
    if options.search_provider != "none" and os.environ.get("OPENAI_API_KEY"):
        try:
            topic_pulse = await _build_topic_pulse(theory, countries, provider)
            notes.append(f"Topic pulse built from {options.search_provider} search snippets.")
        except Exception as exc:
            notes.append(f"Topic pulse unavailable: {exc}")
    else:
        notes.append("Topic pulse unavailable because no search provider was configured.")

    return CurrentWorldState(
        theory=theory,
        country_stats=stats,
        topic_pulse=topic_pulse,
        notes=notes,
    )


def _ideology_bucket(ideology: float) -> str:
    if ideology <= -0.2:
        return "left"
    if ideology >= 0.2:
        return "right"
    return "center"


def _topic_sentiment_for_agent(agent: AgentProfile, pulse: TopicPulse) -> float:
    ideology_bucket = _ideology_bucket(agent.political_ideology)
    ideology_sentiment = {
        "left": pulse.left_sentiment,
        "center": pulse.center_sentiment,
        "right": pulse.right_sentiment,
    }[ideology_bucket]
    country_sentiment = pulse.country_sentiments.get(agent.country, ideology_sentiment)
    return max(-1.0, min(1.0, ideology_sentiment * 0.6 + country_sentiment * 0.4))


def calibrate_world_from_current_state(
    agents: list[AgentProfile],
    current_state: CurrentWorldState | None,
) -> None:
    if not current_state or not current_state.country_stats:
        return

    represented_countries = {
        a.country for a in agents if a.country in current_state.country_stats
    }
    total_population = sum(
        current_state.country_stats[c].population_total or 0.0 for c in represented_countries
    )

    if total_population > 0:
        current_total_weight = sum(a.representational_weight for a in agents)
        for country in represented_countries:
            country_agents = [a for a in agents if a.country == country]
            current_country_weight = sum(a.representational_weight for a in country_agents) or 1
            country_population = current_state.country_stats[country].population_total or 0.0
            target_country_weight = current_total_weight * (country_population / total_population)
            country_scale = target_country_weight / current_country_weight
            for agent in country_agents:
                agent.representational_weight = max(1, round(agent.representational_weight * country_scale))

    for country in represented_countries:
        stats = current_state.country_stats[country]
        if stats.urban_pct is None:
            continue
        urban_ratio = max(0.0, min(1.0, stats.urban_pct / 100.0))
        suburban_target = min(0.25, urban_ratio * 0.3)
        targets = {
            "urban": max(0.05, urban_ratio - suburban_target),
            "suburban": max(0.05, suburban_target),
            "rural": max(0.05, 1.0 - urban_ratio),
        }
        country_agents = [a for a in agents if a.country == country]
        total_weight = sum(a.representational_weight for a in country_agents) or 1
        actual = {}
        for city_type in ("urban", "suburban", "rural"):
            actual[city_type] = (
                sum(a.representational_weight for a in country_agents if a.city_type == city_type) / total_weight
            ) or 0.01
        for agent in country_agents:
            multiplier = targets.get(agent.city_type, 1.0) / max(actual.get(agent.city_type, 0.01), 0.01)
            agent.representational_weight = max(1, round(agent.representational_weight * multiplier))

    pulse = current_state.topic_pulse
    if not pulse:
        return

    for agent in agents:
        topic_sentiment = _topic_sentiment_for_agent(agent, pulse)
        agent.current_beliefs[pulse.topic_key] = topic_sentiment

        country_stats = current_state.country_stats.get(agent.country)
        if country_stats:
            inflation = country_stats.inflation or 0.0
            unemployment = country_stats.unemployment or 0.0
            stress = min(1.0, max(0.0, (inflation / 12.0) * 0.45 + (unemployment / 20.0) * 0.55))
            trust_adjustment = (0.5 - stress) * 0.15
            agent.trust_in_institutions = max(
                0.0,
                min(1.0, agent.trust_in_institutions + trust_adjustment),
            )
            agent.political_efficacy = max(
                0.0,
                min(1.0, agent.political_efficacy + (0.45 - stress) * 0.12),
            )
            agent.change_fatigue = max(
                0.0,
                min(1.0, agent.change_fatigue + stress * 0.18),
            )
            agent.status_quo_bias = max(
                0.0,
                min(1.0, agent.status_quo_bias + stress * 0.1),
            )

            if topic_sentiment <= -0.35 and stress >= 0.45:
                agent.emotional_state = "anxious"
            elif topic_sentiment >= 0.35 and stress <= 0.35:
                agent.emotional_state = "hopeful"


def classify_scenario(theory: str) -> str:
    text = theory.lower()

    if any(term in text for term in ("tariff", "ubi", "subsidy", "tax", "rate hike", "interest rate", "export control", "export restriction", "regulation", "central bank", "policy")):
        return "policy shock"
    if any(term in text for term in ("stock", "market", "bank run", "recession", "inflation", "credit", "fuel shock", "energy price", "commodity")):
        return "market shock"
    if any(term in text for term in ("war", "military", "invasion", "sanction", "geopolitical", "border", "missile", "embargo")):
        return "geopolitical event"
    if any(term in text for term in ("grid", "blackout", "cyber", "internet outage", "port closure", "supply chain", "shipping", "infrastructure")):
        return "infrastructure disruption"
    if any(term in text for term in ("ban", "compliance", "mandate", "restriction", "licensing")):
        return "regulatory intervention"
    return "strategic shock"


def assess_current_world_state(current_state: CurrentWorldState | None) -> BaselineAssessment:
    if not current_state:
        return BaselineAssessment(
            scenario_classification="strategic shock",
            observed_signal_count=0,
            inferred_signal_count=0,
            country_coverage_ratio=0.0,
            baseline_confidence="low",
            source_count=0,
            observed_state=["No baseline data loaded."],
            inferred_state=["No inferred state available."],
        )

    is_static_mode = any("Static world-state mode selected" in note for note in current_state.notes)

    observed_signal_count = 0
    countries_with_any_signal = 0
    observed_state: list[str] = []

    for row in sorted(current_state.country_stats.values(), key=lambda item: item.country):
        available_metrics = [
            row.population_total,
            row.urban_pct,
            row.gdp_growth,
            row.inflation,
            row.unemployment,
            row.gdp_per_capita_usd,
        ]
        non_null_metrics = sum(1 for value in available_metrics if value is not None)
        observed_signal_count += non_null_metrics
        if non_null_metrics:
            countries_with_any_signal += 1
            if len(observed_state) < 6:
                observed_state.append(
                    f"{row.country}: pop={_fmt(row.population_total)}, urban={_fmt(row.urban_pct)}%, "
                    f"gdp_growth={_fmt(row.gdp_growth)}%, inflation={_fmt(row.inflation)}%, "
                    f"unemployment={_fmt(row.unemployment)}%"
                )

    inferred_state: list[str] = []
    inferred_signal_count = 0
    source_count = 1 if current_state.country_stats else 0

    if current_state.topic_pulse:
        pulse = current_state.topic_pulse
        source_count += len(pulse.source_urls)
        ideology_signals = [
            pulse.left_sentiment,
            pulse.center_sentiment,
            pulse.right_sentiment,
        ]
        inferred_signal_count += len(ideology_signals)
        inferred_signal_count += len(pulse.country_sentiments)
        inferred_signal_count += len(pulse.key_narratives)
        inferred_signal_count += len(pulse.economic_channels)

        inferred_state.append(
            f"Public discourse pulse `{pulse.topic_key}`: left={pulse.left_sentiment:+.2f}, "
            f"center={pulse.center_sentiment:+.2f}, right={pulse.right_sentiment:+.2f}"
        )
        for narrative in pulse.key_narratives[:3]:
            inferred_state.append(f"Narrative: {narrative}")
        for channel in pulse.economic_channels[:2]:
            inferred_state.append(f"Economic channel: {channel}")
    else:
        inferred_state.append("No topic-specific discourse reconstruction was available.")

    total_countries = max(1, len(current_state.country_stats))
    country_coverage_ratio = countries_with_any_signal / total_countries

    if is_static_mode:
        baseline_confidence = "scenario-only"
        if not observed_state or observed_state == ["No observed state available."]:
            observed_state = [
                "Static archetype baseline only; live macro indicators were not loaded.",
            ]
        if inferred_state == ["No topic-specific discourse reconstruction was available."]:
            inferred_state = [
                "Scenario entered without live discourse reconstruction; simulation uses archetype defaults plus theory injection.",
            ]
    elif country_coverage_ratio >= 0.8 and observed_signal_count >= 24:
        baseline_confidence = "high"
    elif country_coverage_ratio >= 0.5 and observed_signal_count >= 12:
        baseline_confidence = "medium"
    else:
        baseline_confidence = "low"

    return BaselineAssessment(
        scenario_classification=classify_scenario(current_state.theory),
        observed_signal_count=observed_signal_count,
        inferred_signal_count=inferred_signal_count,
        country_coverage_ratio=country_coverage_ratio,
        baseline_confidence=baseline_confidence,
        source_count=source_count,
        observed_state=observed_state or ["No observed state available."],
        inferred_state=inferred_state,
    )


def format_current_world_state(current_state: CurrentWorldState | None) -> str:
    if not current_state:
        return "No current world-state object available."

    assessment = assess_current_world_state(current_state)
    lines = [
        "Current World State Reconstruction",
        f"- Scenario class: {assessment.scenario_classification}",
    ]
    if assessment.baseline_confidence == "scenario-only":
        lines.append(
            "- Baseline confidence: scenario-only (static archetype mode without live observed-state reconstruction)"
        )
    else:
        lines.append(
            f"- Baseline confidence: {assessment.baseline_confidence} "
            f"({assessment.country_coverage_ratio * 100:.0f}% country coverage, "
            f"{assessment.observed_signal_count} observed signals, "
            f"{assessment.inferred_signal_count} inferred signals)"
        )
    lines.extend([
        f"- Source count: {assessment.source_count}",
        "- Observed state:",
    ])
    lines.extend(f"  - {line}" for line in assessment.observed_state[:6])
    lines.append("- Inferred state:")
    lines.extend(f"  - {line}" for line in assessment.inferred_state[:6])
    if current_state.notes:
        lines.append("- Data notes:")
        lines.extend(f"  - {note}" for note in current_state.notes[:6])

    return "\n".join(lines)


def _fmt(value: float | None) -> str:
    if value is None:
        return "n/a"
    if abs(value) >= 1_000_000:
        return f"{value:,.0f}"
    return f"{value:.2f}"


# Backwards-compatible aliases for the first implementation pass.
GroundingOptions = WorldStateOptions
GroundingBundle = CurrentWorldState
build_grounding_bundle = build_current_world_state
format_grounding_summary = format_current_world_state
calibrate_world = calibrate_world_from_current_state
