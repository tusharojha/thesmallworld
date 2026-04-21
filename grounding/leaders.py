import json
import os
from dataclasses import asdict, dataclass, field

from openai import AsyncOpenAI

from agents.profile import AgentProfile
from grounding.baseline import WorldStateOptions, classify_scenario
from grounding.search import SearchProvider, SearchResult, build_search_provider


DEFAULT_LEADERSHIP_COUNTRIES = [
    "USA",
    "China",
    "India",
    "UK",
    "Germany",
    "France",
    "Russia",
    "Japan",
]


@dataclass
class NamedActorProfile:
    name: str
    title: str
    country: str
    institution: str
    role_type: str
    current_priorities: list[str] = field(default_factory=list)
    typical_response_style: str = ""
    constraints: list[str] = field(default_factory=list)
    ideology_estimate: float = 0.0
    decisiveness: float = 0.5
    trust_signal: float = 0.5
    likely_media_channels: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)
    confidence: str = "medium"


@dataclass
class LeadershipGroundingBundle:
    theory: str
    scenario_classification: str
    actors: list[NamedActorProfile] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    source_count: int = 0


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )


def _model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def should_ground_named_actors(theory: str, decision_lens: str) -> bool:
    scenario_class = classify_scenario(theory)
    return (
        decision_lens in {"government", "central-bank", "ngo", "enterprise-strategy"}
        or scenario_class in {"policy shock", "market shock", "geopolitical event", "regulatory intervention"}
    )


def _relevant_countries(theory: str, available_countries: list[str]) -> list[str]:
    theory_lower = theory.lower()
    mentioned = [country for country in available_countries if country.lower() in theory_lower]
    if mentioned:
        base = mentioned
    else:
        base = [country for country in DEFAULT_LEADERSHIP_COUNTRIES if country in available_countries]
    return base[:6]


def _queries_for_country(country: str, scenario_classification: str, decision_lens: str) -> list[str]:
    queries = [
        f"current head of government {country} official government",
        f"current finance minister {country} official government",
    ]
    if scenario_classification in {"policy shock", "geopolitical event", "regulatory intervention"}:
        queries.append(f"current foreign minister {country} official government")
    if decision_lens == "central-bank" or scenario_classification == "market shock":
        queries.append(f"current central bank governor {country} official")
    return queries


def _gather_results(
    provider: SearchProvider,
    countries: list[str],
    scenario_classification: str,
    decision_lens: str,
) -> list[SearchResult]:
    results: list[SearchResult] = []
    seen_urls: set[str] = set()
    for country in countries:
        for query in _queries_for_country(country, scenario_classification, decision_lens):
            for item in provider.search(query, count=3):
                if item.url in seen_urls:
                    continue
                seen_urls.add(item.url)
                results.append(item)
    return results


async def build_leadership_grounding(
    theory: str,
    available_countries: list[str],
    options: WorldStateOptions,
    decision_lens: str,
) -> LeadershipGroundingBundle:
    scenario_classification = classify_scenario(theory)
    bundle = LeadershipGroundingBundle(
        theory=theory,
        scenario_classification=scenario_classification,
    )

    if not should_ground_named_actors(theory, decision_lens):
        bundle.notes.append("Scenario type did not require named institutional actors.")
        return bundle

    provider = build_search_provider(
        options.search_provider,
        brave_api_key=options.brave_api_key,
        searxng_base_url=options.searxng_base_url,
    )
    if provider.__class__.__name__ == "NullSearchProvider":
        bundle.notes.append("Named leadership grounding skipped because no search provider was configured.")
        return bundle

    if not os.environ.get("OPENAI_API_KEY"):
        bundle.notes.append("Named leadership grounding skipped because OPENAI_API_KEY is not configured.")
        return bundle

    countries = _relevant_countries(theory, available_countries)
    search_results = _gather_results(provider, countries, scenario_classification, decision_lens)
    bundle.source_count = len(search_results)
    if not search_results:
        bundle.notes.append("No leadership search results were returned.")
        return bundle

    snippets = "\n".join(
        f"- {item.title}\n  URL: {item.url}\n  Snippet: {item.snippet}"
        for item in search_results[:24]
    )

    response = await _client().chat.completions.create(
        model=_model(),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are grounding a geopolitical and policy simulation with current real-world leadership. "
                    "Return JSON with key 'actors' containing 4-10 objects. "
                    "Each object must contain: name, title, country, institution, role_type, current_priorities, "
                    "typical_response_style, constraints, ideology_estimate, decisiveness, trust_signal, "
                    "likely_media_channels, confidence. "
                    "Use only the supplied snippets. If uncertain, lower confidence and keep the claim conservative."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Theory: {theory}\n"
                    f"Scenario class: {scenario_classification}\n"
                    f"Decision lens: {decision_lens}\n"
                    f"Target countries: {', '.join(countries)}\n\n"
                    f"Search snippets:\n{snippets}"
                ),
            },
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    raw = json.loads(response.choices[0].message.content)
    actors: list[NamedActorProfile] = []
    for item in raw.get("actors", [])[:10]:
        related_urls = [
            result.url
            for result in search_results
            if item.get("country", "") in result.title or item.get("country", "") in result.snippet
        ][:6]
        actors.append(NamedActorProfile(
            name=str(item.get("name", "")).strip(),
            title=str(item.get("title", "")).strip(),
            country=str(item.get("country", "")).strip(),
            institution=str(item.get("institution", "")).strip() or "government",
            role_type=str(item.get("role_type", "")).strip() or "executive",
            current_priorities=[str(x) for x in item.get("current_priorities", [])[:4]],
            typical_response_style=str(item.get("typical_response_style", "")).strip(),
            constraints=[str(x) for x in item.get("constraints", [])[:4]],
            ideology_estimate=max(-1.0, min(1.0, float(item.get("ideology_estimate", 0.0)))),
            decisiveness=max(0.0, min(1.0, float(item.get("decisiveness", 0.5)))),
            trust_signal=max(0.0, min(1.0, float(item.get("trust_signal", 0.5)))),
            likely_media_channels=[str(x) for x in item.get("likely_media_channels", [])[:4]],
            source_urls=related_urls,
            confidence=str(item.get("confidence", "medium")).strip() or "medium",
        ))

    bundle.actors = [actor for actor in actors if actor.name and actor.country]
    if bundle.actors:
        bundle.notes.append(f"Grounded {len(bundle.actors)} named leadership and institutional actors from live search results.")
    else:
        bundle.notes.append("Leadership search results were available, but no conservative actor dossiers could be extracted.")
    return bundle


def leadership_agents(bundle: LeadershipGroundingBundle) -> list[AgentProfile]:
    profiles: list[AgentProfile] = []
    for idx, actor in enumerate(bundle.actors, start=1):
        media_sources = actor.likely_media_channels or ["public_broadcaster", "online_news"]
        profile = AgentProfile(
            id=f"leader_{idx:02d}_{actor.country.lower().replace(' ', '_')}",
            name=actor.name,
            age=56,
            gender="non-binary",
            country=actor.country,
            city_type="urban",
            income_bracket="high",
            education_level="postgrad",
            occupation=actor.title.lower(),
            political_ideology=actor.ideology_estimate,
            religious_affiliation="other",
            religiosity_level=0.1,
            trust_in_institutions=max(0.35, min(0.95, actor.trust_signal)),
            openness_to_change=max(0.15, min(0.9, 0.6 - actor.decisiveness * 0.15 + (0.1 if actor.role_type == "central_bank" else 0.0))),
            openness=0.65,
            conscientiousness=0.9,
            extraversion=max(0.45, min(0.85, 0.45 + actor.decisiveness * 0.35)),
            agreeableness=max(0.25, min(0.75, 0.6 - abs(actor.ideology_estimate) * 0.15)),
            neuroticism=0.25,
            media_trust=0.8,
            political_efficacy=0.95,
            change_fatigue=0.25,
            conflict_orientation=max(0.25, min(0.9, 0.25 + actor.decisiveness * 0.3)),
            social_trust=0.55,
            status_quo_bias=max(0.35, min(0.9, 0.5 + actor.trust_signal * 0.2)),
            media_sources=media_sources,
            representational_weight=1,
        )
        summary_bits = []
        if actor.current_priorities:
            summary_bits.append("Priorities: " + ", ".join(actor.current_priorities[:3]))
        if actor.typical_response_style:
            summary_bits.append("Response style: " + actor.typical_response_style)
        if actor.constraints:
            summary_bits.append("Constraints: " + ", ".join(actor.constraints[:2]))
        if summary_bits:
            profile.memory.append({"step": 0, "summary": " | ".join(summary_bits)})
        profiles.append(profile)
    return profiles


def format_leadership_grounding(bundle: LeadershipGroundingBundle) -> str:
    lines = ["Leadership and Institutional Grounding"]
    if not bundle.actors:
        lines.extend(f"- {note}" for note in bundle.notes[:4])
        return "\n".join(lines)

    lines.append(f"- Scenario class: {bundle.scenario_classification}")
    lines.append(f"- Named actors: {len(bundle.actors)}")
    lines.append(f"- Search sources used: {bundle.source_count}")
    for note in bundle.notes[:4]:
        lines.append(f"- {note}")
    for actor in bundle.actors[:6]:
        lines.append(
            f"- {actor.country}: {actor.name}, {actor.title} | style={actor.typical_response_style or 'n/a'} | "
            f"confidence={actor.confidence}"
        )
    return "\n".join(lines)


def leadership_bundle_jsonable(bundle: LeadershipGroundingBundle) -> dict[str, object]:
    return {
        "theory": bundle.theory,
        "scenario_classification": bundle.scenario_classification,
        "source_count": bundle.source_count,
        "notes": bundle.notes,
        "actors": [asdict(actor) for actor in bundle.actors],
    }
