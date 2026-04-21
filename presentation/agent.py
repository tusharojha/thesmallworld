import os
import shutil
import subprocess
from pathlib import Path

from simulation.engine import SimulationLog


async def generate_presentation(log: SimulationLog, report_md: str) -> str:
    executive = _extract_bullets(report_md, "## 1. Executive Snapshot", 5)
    baseline = _extract_bullets(report_md, "## 2. Current World State Reconstruction", 5)
    leadership = _extract_bullets(report_md, "## 3. Leadership And Institutional Response", 5)
    stress_map = _extract_bullets(report_md, "## 4. System Stress Map", 5)
    propagation = _extract_bullets(report_md, "## 5. Shock Propagation", 4)
    indicators = _extract_bullets(report_md, "## 6. Leading Indicators", 4)
    signals = _extract_bullets(report_md, "## 7. Representative Signals", 4)

    cascades = sorted(
        log.cascades,
        key=lambda c: (len(c.influenced_agents), len(c.edges)),
        reverse=True,
    )[:3]
    latest = log.world_state.history[-1] if log.world_state.history else None

    slides: list[str] = []
    slides.append(_frontmatter(log))
    slides.append(_title_slide(log))

    snapshot_lines = [
        f"- Scenario class: {log.scenario_classification or 'strategic shock'}",
        f"- Decision lens: {log.decision_lens or 'general'}",
        f"- Weeks simulated: {log.steps_run}",
        f"- Emergent events: {len(log.emergent_events)}",
        f"- Cascade traces: {len(log.cascades)}",
        f"- Baseline confidence: {log.baseline_confidence or 'unknown'}",
    ]
    if latest:
        snapshot_lines.extend([
            f"- Final polarization: {latest.political_polarization:.2f}",
            f"- Avg economic stress: {_avg_stress(latest):.2f}",
        ])
    slides.append(_slide("Decision Snapshot", snapshot_lines))

    slides.append(_slide("Executive Judgments", executive or ["- No strong findings recorded."]))
    slides.append(_slide("Current World State", baseline or ["- No baseline reconstruction recorded."]))
    slides.append(_slide("Leadership Response", leadership or ["- No named leadership actors were grounded."]))
    slides.append(_slide("System Stress Map", stress_map or ["- No system stress map recorded."]))
    slides.append(_slide("Shock Propagation", propagation or ["- No propagation paths recorded."]))

    if cascades:
        for idx, cascade in enumerate(cascades, start=1):
            slides.append(_slide(
                f"Butterfly Effect {idx}",
                [
                    f"- Origin: {cascade.origin_label}",
                    f"- Topic: {cascade.topic}",
                    f"- Direct recipients: {len(cascade.direct_recipients)}",
                    f"- Total influenced: {len(cascade.influenced_agents)}",
                    f"- Activated edges: {len(cascade.edges)}",
                    "- Interpretation: local reactions propagated through explicit graph paths rather than a global broadcast.",
                ],
            ))

    slides.append(_slide("Leading Indicators", indicators or ["- No leading indicators recorded."]))
    slides.append(_slide("Representative Signals", signals or ["- No representative signal lines recorded."]))
    slides.append(_slide("Decision Use", [
        f"- Frame actions through the `{log.decision_lens or 'general'}` lens.",
        "- Use this as a stress test, not as a literal forecast.",
        "- Watch for early high-centrality cascades and low-trust or high-fatigue clusters.",
        "- Compare interventions against the same reconstructed current world state.",
    ]))

    return "\n\n---\n\n".join(slides).strip() + "\n"


async def generate_video_brief(log: SimulationLog, report_md: str) -> str:
    top_findings = _extract_bullets(report_md, "## 1. Executive Snapshot", 4)
    indicators = _extract_bullets(report_md, "## 5. Leading Indicators", 3)
    cascades = sorted(
        log.cascades,
        key=lambda c: (len(c.influenced_agents), len(c.edges)),
        reverse=True,
    )[:2]

    lines = [
        "# Video Brief",
        "",
        "## Goal",
        "",
        f"- Explain how `{log.theory}` changes the reconstructed current world state.",
        "- Focus on second-order effects, not only direct reactions.",
        f"- Frame takeaways for a `{log.decision_lens or 'general'}` audience.",
        "",
        "## Runtime Options",
        "",
        "- Short cut: 30 seconds",
        "- Full cut: 60 seconds",
        "",
        "## Scene List",
        "",
        "1. Reconstructed current world state",
        "2. Shock classification and injection",
        "3. First-wave reactions",
        "4. Graph cascades / butterfly effects",
        "5. System stress concentration",
        "6. Final decision takeaway",
        "",
        "## Voiceover Script",
        "",
        *top_findings,
        *indicators,
        "",
        "## Data Visuals",
        "",
    ]
    for cascade in cascades:
        lines.append(
            f"- Cascade `{cascade.origin_label} -> {cascade.topic}` with {len(cascade.influenced_agents)} influenced agents and {len(cascade.edges)} activated edges."
        )
    lines.extend([
        "",
        "## Remotion Build Notes",
        "",
        "- Use graph lines to animate propagation hop by hop.",
        "- Keep labels sparse and emphasize 2-3 dominant paths only.",
        "- Color-code tension: green for stabilizing, yellow for anxious, red for conflict-amplifying.",
        "",
    ])
    return "\n".join(lines)


def render_with_marp(deck_path: str, output_path: str | None = None, fmt: str = "pdf") -> subprocess.CompletedProcess:
    local_marp = Path("node_modules/.bin/marp")
    marp_binary = str(local_marp) if local_marp.exists() else shutil.which("marp")
    if marp_binary:
        command = [marp_binary, deck_path]
    else:
        command = ["npx", "@marp-team/marp-cli@latest", deck_path]

    if fmt == "pdf":
        command.append("--pdf")
    elif fmt == "pptx":
        command.append("--pptx")
    elif fmt == "html":
        pass
    else:
        raise ValueError(f"Unsupported Marp output format: {fmt}")

    if output_path:
        command.extend(["-o", output_path])

    browser_path = _browser_path()
    if browser_path and fmt == "pdf":
        command.extend(["--browser-path", browser_path])

    return subprocess.run(command, check=False, capture_output=True, text=True)


def render_command(deck_path: str, output_path: str, fmt: str = "pdf") -> str:
    local_marp = Path("node_modules/.bin/marp")
    if local_marp.exists():
        command = [str(local_marp), deck_path]
    else:
        command = ["npx", "@marp-team/marp-cli@latest", deck_path]
    if fmt == "pdf":
        command.append("--pdf")
    elif fmt == "pptx":
        command.append("--pptx")
    elif fmt == "html":
        pass
    command.extend(["-o", output_path])
    browser_path = _browser_path()
    if browser_path and fmt == "pdf":
        command.extend(["--browser-path", browser_path])
    return " ".join(command)


def _frontmatter(log: SimulationLog) -> str:
    return "\n".join([
        "---",
        "marp: true",
        "paginate: true",
        "theme: default",
        "style: |",
        "  section {",
        "    font-family: 'Avenir Next', 'Segoe UI', sans-serif;",
        "    background: linear-gradient(135deg, #f8f5ef 0%, #e7ecef 100%);",
        "    color: #1d2830;",
        "    padding: 56px;",
        "  }",
        "  h1, h2, h3 { color: #17324d; }",
        "  strong { color: #8d3b1f; }",
        "  code { background: rgba(23, 50, 77, 0.08); padding: 0.1em 0.25em; }",
        "  ul { font-size: 1.05rem; line-height: 1.45; }",
        "  section.lead {",
        "    background: radial-gradient(circle at top left, #f2d3a2 0%, #f8f5ef 36%, #d9e7ee 100%);",
        "  }",
        "  section.darkband {",
        "    background: linear-gradient(120deg, #17324d 0%, #244b68 100%);",
        "    color: #f4f0e8;",
        "  }",
        "---",
    ])


def _title_slide(log: SimulationLog) -> str:
    return "\n".join([
        "<!-- _class: lead -->",
        "# The Small World",
        "",
        "## Current-State-Grounded Scenario Deck",
        "",
        f"**Theory:** {log.theory}",
    ])


def _slide(title: str, bullets: list[str]) -> str:
    cleaned = [line if line.startswith("- ") else f"- {line}" for line in bullets if line]
    return "\n".join([f"## {title}", "", *cleaned])


def _extract_bullets(report_md: str, heading: str, limit: int) -> list[str]:
    if heading not in report_md:
        return []
    section = report_md.split(heading, 1)[1]
    stop_markers = ["\n## ", "\n---"]
    stop_positions = [section.find(marker) for marker in stop_markers if section.find(marker) != -1]
    if stop_positions:
        section = section[:min(stop_positions)]
    lines = [line.strip() for line in section.splitlines() if line.strip().startswith("- ")]
    return lines[:limit]


def _avg_stress(snapshot) -> float:
    return (
        sum(snapshot.economic_stress.values()) / len(snapshot.economic_stress)
        if snapshot.economic_stress else 0.0
    )


def _browser_path() -> str | None:
    candidates = [
        "node_modules/.bin/chrome",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None
