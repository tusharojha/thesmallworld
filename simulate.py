#!/usr/bin/env python3
"""
The Small World — live simulation dashboard.

Usage:
  python simulate.py --theory "UBI of $2000/month introduced globally" --steps 10
  python simulate.py --theory "AGI is announced tomorrow" --steps 5 --concurrency 10
"""
import argparse
import asyncio
import os
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

load_dotenv()

console = Console()

# ── Emotion → display color ───────────────────────────────────────────────────
EMOTION_COLOR = {
    "hopeful":     "green",
    "excited":     "bright_green",
    "determined":  "cyan",
    "neutral":     "white",
    "anxious":     "yellow",
    "resigned":    "dim white",
    "fearful":     "dark_orange",
    "angry":       "red",
}

EMOTION_DOT = {
    "hopeful":     ("●", "green"),
    "excited":     ("●", "bright_green"),
    "determined":  ("●", "cyan"),
    "neutral":     ("●", "white"),
    "anxious":     ("●", "yellow"),
    "resigned":    ("●", "dim white"),
    "fearful":     ("●", "dark_orange"),
    "angry":       ("●", "red"),
}


def _bar(value: float, width: int = 14) -> Text:
    value = max(0.0, min(1.0, value))
    filled = int(value * width)
    t = Text()
    t.append("█" * filled, style="green")
    t.append("░" * (width - filled), style="dim")
    return t


def _elapsed(start: float) -> str:
    s = int(time.time() - start)
    m, s = divmod(s, 60)
    return f"{m:02d}:{s:02d}"


# ── Dashboard state & rendering ───────────────────────────────────────────────
class SimulationDashboard:
    def __init__(
        self,
        agents,
        theory: str,
        n_steps: int,
        scenario_classification: str = "",
        decision_lens: str = "",
        baseline_confidence: str = "",
    ):
        self.theory = theory
        self.n_steps = n_steps
        self.total_agents = len(agents)
        self.start_time = time.time()
        self.current_step = 0
        self.agents_done_this_step = 0
        self._live = None
        self.scenario_classification = scenario_classification
        self.decision_lens = decision_lens
        self.baseline_confidence = baseline_confidence

        # Per-agent display state
        self.agent_states: dict[str, dict] = {
            a.id: {
                "name": a.name,
                "country": a.country,
                "status": "pending",   # pending | processing | done
                "emotion": "neutral",
                "snippet": "",
                "updated_at": 0.0,
            }
            for a in agents
        }

        # Feed: list of (kind, text) tuples
        # kind: "convo_header" | "convo_line" | "emergent" | "step_summary" | "reaction"
        self.feed: deque[tuple[str, str]] = deque(maxlen=300)

        # Active streaming buffers: "{a}×{b}" -> accumulated text so far
        self.stream_buffers: dict[str, str] = {}
        self.stream_order: list[str] = []   # insertion order for display

        # World state (updated per step)
        self.polarization: float = 0.0
        self.econ_stress: dict[str, float] = {}
        self.top_beliefs: dict[str, float] = {}
        self.emergent_count: int = 0
        self.event_log: list[str] = []

        self.layout = self._build_layout()

    def set_live(self, live):
        self._live = live

    def _refresh(self):
        self._render_all()
        if self._live:
            self._live.refresh()

    # ── Callbacks called by the simulation engine ─────────────────────────────

    def on_agent_start(self, agent_id: str):
        if agent_id in self.agent_states:
            s = self.agent_states[agent_id]
            s["status"] = "processing"
            s["updated_at"] = time.time()
        self._refresh()

    def on_agent_complete(self, agent_id: str, emotion: str, snippet: str):
        if agent_id in self.agent_states:
            s = self.agent_states[agent_id]
            s["status"] = "done"
            s["emotion"] = emotion
            s["snippet"] = snippet[:70].replace("\n", " ")
            s["updated_at"] = time.time()
            self.agents_done_this_step += 1
        self._refresh()

    def on_conversation_chunk(self, a_name: str, b_name: str, topic: str, chunk: str):
        key = f"{a_name} × {b_name}"
        if key not in self.stream_buffers:
            self.stream_buffers[key] = ""
            self.stream_order.append(key)
            # Header into the feed
            self.feed.append(("convo_header", f"Wk {self.current_step}  {key}  [{topic[:28]}]"))
        self.stream_buffers[key] += chunk
        self._refresh()

    def on_emergent_event(self, event):
        self.emergent_count += 1
        desc = event.description[:72]
        self.feed.append(("emergent", f"[{event.topic}]  {desc}"))
        self.event_log.append(f"Wk {event.step_introduced}: {event.topic} — {event.description[:60]}")
        self._refresh()

    def on_step_start(self, step: int):
        self.current_step = step
        self.agents_done_this_step = 0
        # Reset agent statuses for the new step (keep emotion from last step)
        for s in self.agent_states.values():
            s["status"] = "pending"
        # Flush completed stream buffers into the feed as completed conversations
        for key in self.stream_order:
            text = self.stream_buffers.get(key, "")
            for line in text.strip().split("\n"):
                line = line.strip()
                if line:
                    self.feed.append(("convo_line", line))
        self.stream_buffers.clear()
        self.stream_order.clear()
        self.feed.append(("step_summary", f"━━━ Week {step} of {self.n_steps} ━━━"))
        self._refresh()

    def on_step_complete(self, step: int, snapshot, conversations):
        self.polarization = snapshot.political_polarization
        # Collect economic stress from country segments
        for seg, stress in snapshot.economic_stress.items():
            if seg in ("USA", "India", "Brazil", "Nigeria", "China", "Germany",
                       "France", "Poland", "Russia", "Japan", "South Korea"):
                self.econ_stress[seg] = stress
        # Aggregate top beliefs
        for seg_beliefs in snapshot.opinion_by_segment.values():
            for topic, val in seg_beliefs.items():
                prev = self.top_beliefs.get(topic, 0.0)
                self.top_beliefs[topic] = (prev + val) / 2
        # Flush any remaining stream text into feed
        for key in self.stream_order:
            text = self.stream_buffers.get(key, "")
            for line in text.strip().split("\n"):
                line = line.strip()
                if line:
                    self.feed.append(("convo_line", line))
        self.stream_buffers.clear()
        self.stream_order.clear()
        self._refresh()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=6),
        )
        layout["body"].split_row(
            Layout(name="agents", ratio=28),
            Layout(name="feed", ratio=44),
            Layout(name="world", ratio=28),
        )
        return layout

    def _render_all(self):
        self.layout["header"].update(self._render_header())
        self.layout["agents"].update(self._render_agents())
        self.layout["feed"].update(self._render_feed())
        self.layout["world"].update(self._render_world())
        self.layout["footer"].update(self._render_footer())

    # ── Header ────────────────────────────────────────────────────────────────

    def _render_header(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="center", ratio=3)
        grid.add_column(justify="right", ratio=1)
        grid.add_row(
            Text("THE SMALL WORLD // DECISION INTELLIGENCE", style="bold cyan"),
            Text(f'"{self.theory[:64]}"', style="dim italic"),
            Text(
                f"{self.scenario_classification or 'scenario'}   Week {self.current_step}/{self.n_steps}   {_elapsed(self.start_time)}",
                style="yellow bold",
            ),
        )
        return Panel(grid, border_style="cyan", padding=(0, 1))

    # ── Agent panel ───────────────────────────────────────────────────────────

    def _render_agents(self) -> Panel:
        table = Table(box=None, padding=(0, 0), show_header=False, expand=True)
        table.add_column(width=2)    # dot
        table.add_column(width=11)   # name
        table.add_column(width=4)    # country ISO
        table.add_column()           # emotion / status

        # Sort: processing → done (most recent first) → pending
        sorted_states = sorted(
            self.agent_states.items(),
            key=lambda kv: (
                {"processing": 0, "done": 1, "pending": 2}[kv[1]["status"]],
                -kv[1]["updated_at"],
            ),
        )

        n_done = sum(1 for _, s in sorted_states if s["status"] == "done")
        n_proc = sum(1 for _, s in sorted_states if s["status"] == "processing")
        n_pend = self.total_agents - n_done - n_proc

        # Show up to 35 rows; summarise the rest
        shown = 0
        for _, state in sorted_states:
            if shown >= 35:
                break
            status = state["status"]
            emotion = state["emotion"]
            country_short = _country_iso(state["country"])

            if status == "processing":
                dot = Text("◉", style="bold yellow blink")
                emo_text = Text("thinking…", style="dim yellow")
            elif status == "done":
                char, color = EMOTION_DOT.get(emotion, ("●", "white"))
                dot = Text(char, style=f"bold {color}")
                emo_text = Text(emotion, style=color)
            else:
                dot = Text("○", style="dim")
                emo_text = Text("—", style="dim")

            table.add_row(dot, Text(state["name"][:11], style="bold" if status == "processing" else ""),
                          Text(country_short, style="dim"), emo_text)
            shown += 1

        if n_pend > 0 and shown >= 35:
            table.add_row(Text("○", style="dim"), Text(f"+{n_pend} pending", style="dim"), "", "")

        title = (
            f"[bold]AGENTS[/bold]  "
            f"[green]{n_done}✓[/green]  "
            f"[yellow]{n_proc}◉[/yellow]  "
            f"[dim]{n_pend}○[/dim]"
        )
        return Panel(table, title=title, border_style="blue", padding=(0, 1))

    # ── Feed panel ────────────────────────────────────────────────────────────

    def _render_feed(self) -> Panel:
        content = Text()

        # Active streams at the top (currently generating)
        if self.stream_buffers:
            for key in self.stream_order:
                buf = self.stream_buffers.get(key, "")
                if not buf:
                    continue
                content.append(f"◈ {key}\n", style="bold cyan")
                # Show last 4 lines of the stream
                lines = buf.split("\n")
                for line in lines[-4:]:
                    if line.strip():
                        content.append(f"  {line[:54]}\n", style="cyan")
            content.append("─" * 46 + "\n", style="dim")

        # Feed history (most recent at bottom — show last ~25 items)
        recent = list(self.feed)[-25:]
        for kind, text in recent:
            if kind == "step_summary":
                content.append(f"\n{text}\n", style="bold white")
            elif kind == "convo_header":
                content.append(f"\n{text}\n", style="bold dim white")
            elif kind == "convo_line":
                content.append(f"  {text[:52]}\n", style="white")
            elif kind == "emergent":
                content.append(f"\n⚡ {text[:54]}\n", style="bold yellow")
            elif kind == "reaction":
                content.append(f"  {text[:52]}\n", style="dim")

        title = f"[bold]CASCADE FEED[/bold]  Week [yellow]{self.current_step}[/yellow]  [dim]({self.emergent_count} emergent events)[/dim]"
        return Panel(content, title=title, border_style="green", padding=(0, 1))

    # ── World panel ───────────────────────────────────────────────────────────

    def _render_world(self) -> Panel:
        content = Text()

        # Polarization
        content.append("Polarization\n", style="bold")
        bar = _bar(self.polarization, width=14)
        content.append_text(bar)
        content.append(f"  {self.polarization:.2f}\n\n")

        # Economic stress by country
        if self.econ_stress:
            content.append("Econ Stress\n", style="bold")
            for country, stress in sorted(self.econ_stress.items(), key=lambda kv: -kv[1])[:7]:
                label = f"{country[:6]:<6}"
                bar = _bar(stress, width=8)
                content.append(f"{label} ", style="dim")
                content.append_text(bar)
                content.append(f"  {stress:.2f}\n")
            content.append("\n")

        # Top belief shifts
        if self.top_beliefs:
            content.append("Beliefs\n", style="bold")
            top = sorted(self.top_beliefs.items(), key=lambda kv: abs(kv[1]), reverse=True)[:6]
            for topic, val in top:
                arrow = "▲" if val >= 0 else "▼"
                color = "green" if val >= 0 else "red"
                label = topic.replace("_", " ")[:12]
                content.append(f"{label:<12} ", style="dim")
                content.append(f"{arrow} {val:+.2f}\n", style=color)
            content.append("\n")

        # Recent emergent events
        if self.event_log:
            content.append("Events\n", style="bold")
            for entry in self.event_log[-4:]:
                content.append(f"⚡ {entry[:26]}\n", style="yellow dim")

        return Panel(content, title="[bold]SYSTEM STATE[/bold]", border_style="magenta", padding=(0, 1))

    # ── Footer ────────────────────────────────────────────────────────────────

    def _render_footer(self) -> Panel:
        content = Text()

        # Overall progress
        overall_pct = self.current_step / self.n_steps if self.n_steps else 0
        content.append("  Overall  ", style="dim")
        content.append_text(_bar(overall_pct, width=32))
        content.append(f"  Week {self.current_step}/{self.n_steps}\n")

        # Per-step agent progress
        agent_pct = self.agents_done_this_step / self.total_agents if self.total_agents else 0
        content.append("  Agents   ", style="dim")
        content.append_text(_bar(agent_pct, width=32))
        content.append(f"  {self.agents_done_this_step}/{self.total_agents}\n")

        # Status line
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        content.append(
            f"\n  Elapsed: {_elapsed(self.start_time)}  │  "
            f"Emergent: {self.emergent_count}  │  "
            f"Lens: {self.decision_lens or 'general'}  │  "
            f"Baseline: {self.baseline_confidence or 'n/a'}  │  "
            f"Model: {model}  │  "
            f"Concurrency: {self._concurrency if hasattr(self, '_concurrency') else '—'}",
            style="dim",
        )

        return Panel(content, border_style="dim", padding=(0, 0))


# ── Helpers ───────────────────────────────────────────────────────────────────

_COUNTRY_ISO: dict[str, str] = {
    "USA": "US", "Canada": "CA", "Australia": "AU",
    "UK": "UK", "Germany": "DE", "France": "FR", "Poland": "PL",
    "Sweden": "SE", "Norway": "NO", "Russia": "RU",
    "India": "IN", "China": "CN", "Japan": "JP", "South Korea": "KR",
    "Nigeria": "NG", "Ghana": "GH", "Ethiopia": "ET",
    "Brazil": "BR", "Mexico": "MX", "Colombia": "CO",
    "Egypt": "EG", "Saudi Arabia": "SA",
    "Thailand": "TH", "Indonesia": "ID",
}

def _country_iso(country: str) -> str:
    return _COUNTRY_ISO.get(country, country[:2].upper())


# ── CLI ───────────────────────────────────────────────────────────────────────

def _check_env():
    if not os.environ.get("OPENAI_API_KEY"):
        console.print("[red]Error:[/red] OPENAI_API_KEY not set. Copy .env.example to .env and fill it in.")
        sys.exit(1)


def _parse_args():
    parser = argparse.ArgumentParser(
        description="The Small World — current-state-grounded decision intelligence engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--theory", "-t", required=True,
                        help='The policy, market, infrastructure, or geopolitical shock to simulate')
    parser.add_argument("--steps", "-s", type=int, default=10,
                        help="Simulation weeks to run (default: 10)")
    parser.add_argument("--concurrency", "-c", type=int, default=20,
                        help="Max parallel LLM calls (default: 20)")
    parser.add_argument("--output", "-o", default=None,
                        help="Output file path (default: report_TIMESTAMP.md)")
    parser.add_argument("--grounding", choices=["static", "live"], default="static",
                        help="Reconstruct the current world state from live data before simulation (default: static)")
    parser.add_argument("--search-provider", choices=["none", "brave", "searxng"], default="none",
                        help="Search provider for topic grounding (default: none)")
    parser.add_argument("--searxng-url", default=os.environ.get("SEARXNG_BASE_URL"),
                        help="Base URL for a SearXNG instance, e.g. https://searx.example.org")
    parser.add_argument("--presentation", action="store_true",
                        help="Generate a Marp presentation deck alongside the report")
    parser.add_argument("--presentation-output", default=None,
                        help="Presentation output path (default: report_TIMESTAMP_slides.md)")
    parser.add_argument("--render-presentation", choices=["pdf", "pptx", "html"], default=None,
                        help="Optionally render the Marp deck through Marp CLI")
    parser.add_argument("--video-brief", action="store_true",
                        help="Generate a video production brief for downstream Remotion/Claude workflows")
    parser.add_argument("--video-brief-output", default=None,
                        help="Video brief output path (default: report_TIMESTAMP_video_brief.md)")
    parser.add_argument("--lens", choices=["government", "central-bank", "ngo", "enterprise-strategy"], default="government",
                        help="Decision-maker lens used to frame outputs (default: government)")
    return parser.parse_args()


async def main():
    _check_env()
    args = _parse_args()

    from agents.world_init import build_world, represented_countries
    from grounding.baseline import (
        WorldStateOptions,
        assess_current_world_state,
        build_current_world_state,
        classify_scenario,
        format_current_world_state,
    )
    from presentation.agent import (
        generate_presentation,
        generate_video_brief,
        render_command,
        render_with_marp,
    )
    from simulation.events import inject_theory
    from simulation.engine import run_simulation
    from report.agent import generate_report

    world_state_options = WorldStateOptions(
        mode=args.grounding,
        search_provider=args.search_provider,
        searxng_base_url=args.searxng_url,
        brave_api_key=os.environ.get("BRAVE_SEARCH_API_KEY"),
    )

    # ── Phase 1: Reconstruct current world state ──────────────────────────────
    console.print("[bold cyan]THE SMALL WORLD[/bold cyan]  initializing...\n")
    console.print("[bold]Reconstructing current world state...[/bold]")
    with console.status(""):
        current_world_state = await build_current_world_state(
            theory=args.theory,
            countries=represented_countries(),
            options=world_state_options,
        )
    current_world_state_summary = format_current_world_state(current_world_state)
    baseline_assessment = assess_current_world_state(current_world_state)
    scenario_classification = classify_scenario(args.theory)
    console.print(current_world_state_summary)
    console.print()

    # ── Phase 2: World init ───────────────────────────────────────────────────
    agents, social_graph = build_world(current_state=current_world_state)
    total_weight = sum(a.representational_weight for a in agents)
    console.print(
        f"  [green]✓[/green] {len(agents)} archetypes  "
        f"(~{total_weight * 1_000_000:,.0f} people represented)\n"
        f"  [green]✓[/green] Social graph: {social_graph.number_of_edges()} connections\n"
    )

    # ── Phase 3: Theory injection ──────────────────────────────────────────────
    console.print("[bold]Parsing theory → initial events...[/bold]")
    with console.status(""):
        initial_events = await inject_theory(args.theory, grounding_context=current_world_state_summary)
    console.print(f"  [green]✓[/green] {len(initial_events)} initial events generated\n")
    for e in initial_events:
        console.print(f"    [cyan]·[/cyan] [bold]{e.topic}[/bold]: {e.description[:72]}")
    console.print()

    # ── Phase 4: Live simulation ───────────────────────────────────────────────
    dashboard = SimulationDashboard(
        agents,
        args.theory,
        args.steps,
        scenario_classification=scenario_classification,
        decision_lens=args.lens,
        baseline_confidence=baseline_assessment.baseline_confidence,
    )
    dashboard._concurrency = args.concurrency
    dashboard._render_all()

    with Live(dashboard.layout, refresh_per_second=12, screen=False, transient=False) as live:
        dashboard.set_live(live)

        sim_log = await run_simulation(
            theory=args.theory,
            agents=agents,
            social_graph=social_graph,
            initial_events=initial_events,
            n_steps=args.steps,
            on_agent_start=dashboard.on_agent_start,
            on_agent_complete=dashboard.on_agent_complete,
            on_conversation_chunk=dashboard.on_conversation_chunk,
            on_emergent_event=dashboard.on_emergent_event,
            on_step_start=dashboard.on_step_start,
            on_step_complete=dashboard.on_step_complete,
            concurrency=args.concurrency,
        )

    # ── Phase 5: Report ────────────────────────────────────────────────────────
    console.print("\n[bold]Generating report…[/bold]")
    sim_log.current_world_state_summary = current_world_state_summary
    sim_log.scenario_classification = scenario_classification
    sim_log.decision_lens = args.lens
    sim_log.baseline_confidence = baseline_assessment.baseline_confidence
    sim_log.baseline_observed_signals = baseline_assessment.observed_signal_count
    sim_log.baseline_inferred_signals = baseline_assessment.inferred_signal_count
    sim_log.baseline_country_coverage = baseline_assessment.country_coverage_ratio
    sim_log.baseline_source_count = baseline_assessment.source_count
    with console.status("Synthesising findings…"):
        report_md = await generate_report(sim_log)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = args.output or f"report_{timestamp}.md"
    Path(output_path).write_text(report_md, encoding="utf-8")

    console.print(f"\n[bold green]✓ Report:[/bold green] {output_path}  (~{len(report_md.split()):,} words)")

    if args.presentation:
        console.print("\n[bold]Generating presentation…[/bold]")
        with console.status("Structuring Marp deck…"):
            deck_md = await generate_presentation(sim_log, report_md)
        deck_path = args.presentation_output or f"report_{timestamp}_slides.md"
        Path(deck_path).write_text(deck_md, encoding="utf-8")
        console.print(f"[bold green]✓ Presentation deck:[/bold green] {deck_path}")

        if args.render_presentation:
            rendered_output = f"{Path(deck_path).with_suffix('')}.{args.render_presentation}"
            console.print(f"[bold]Rendering deck with Marp CLI → {args.render_presentation}…[/bold]")
            result = render_with_marp(deck_path, rendered_output, fmt=args.render_presentation)
            if result.returncode == 0:
                console.print(f"[bold green]✓ Rendered deck:[/bold green] {rendered_output}")
            else:
                console.print("[yellow]Marp render failed.[/yellow]")
                if result.stderr:
                    console.print(result.stderr[:800])
                console.print("[bold]Run this manually:[/bold]")
                console.print(render_command(deck_path, rendered_output, fmt=args.render_presentation))

    if args.video_brief:
        console.print("\n[bold]Generating video brief…[/bold]")
        with console.status("Writing production brief…"):
            video_brief = await generate_video_brief(sim_log, report_md)
        video_brief_path = args.video_brief_output or f"report_{timestamp}_video_brief.md"
        Path(video_brief_path).write_text(video_brief, encoding="utf-8")
        console.print(f"[bold green]✓ Video brief:[/bold green] {video_brief_path}")

    if sim_log.emergent_events:
        console.print("\n[bold]Emergent events:[/bold]")
        for e in sim_log.emergent_events[:10]:
            console.print(f"  Wk {e.step_introduced}  [cyan]{e.topic}[/cyan] — {e.description[:68]}")


if __name__ == "__main__":
    asyncio.run(main())
