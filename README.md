# The Small World

The Small World is a world simulator for testing real-world theories across thousands of agents.

It reconstructs a current-state baseline, injects a shock, propagates the effects through a social graph of populations and institutions, and produces decision-oriented outputs such as reports, decks, video briefs, and saved world artifacts.

## What It Does

- Reconstructs a baseline world state from country indicators and optional live discourse signals.
- Builds a population of archetype agents calibrated to that baseline.
- Optionally grounds named leaders and institutions for serious policy and geopolitical scenarios.
- Injects a theory such as tariffs, export controls, UBI, sanctions, droughts, or infrastructure failures.
- Simulates how effects propagate through explicit relationships, conversations, and emergent events.
- Produces outputs you can read immediately or inspect later from a saved artifact.

## Outputs

A run can generate:

- A Markdown report
- A saved world artifact JSON
- A Marp slide deck
- A rendered presentation in `pdf`, `pptx`, or `html`
- A video production brief

The saved artifact can also be inspected, searched, and queried after the run finishes.

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Required:

- `OPENAI_API_KEY`

Optional:

- `OPENAI_BASE_URL`
- `OPENAI_MODEL`
- `BRAVE_SEARCH_API_KEY`
- `SEARXNG_BASE_URL`

### 3. Run a simulation

```bash
python simulate.py run \
  --theory "A major semiconductor export restriction is introduced" \
  --steps 8 \
  --grounding live \
  --search-provider brave \
  --lens government \
  --named-actors auto \
  --presentation \
  --video-brief
```

If you omit `run`, the CLI defaults to the run command, so this also works:

```bash
python simulate.py \
  --theory "A major semiconductor export restriction is introduced" \
  --steps 8
```

## Core Commands

### Run

```bash
python simulate.py run --theory "The EU agrees a carbon-border levy overnight"
```

Useful flags:

- `--grounding static|live` controls whether the run uses archetype defaults or reconstructs a current-world baseline first.
- `--search-provider none|brave|searxng` adds optional live discourse grounding.
- `--searxng-url` sets the SearXNG base URL when using `searxng`.
- `--steps` controls simulated weeks.
- `--concurrency` controls parallel LLM calls.
- `--lens government|central-bank|ngo|enterprise-strategy` changes how outputs are framed.
- `--named-actors auto|off` controls whether named leaders and institutions are grounded.
- `--presentation` writes a Marp deck.
- `--render-presentation pdf|pptx|html` renders the deck via Marp CLI.
- `--video-brief` writes a downstream video brief.
- `--artifact-output` sets the saved world artifact path.

### Inspect an artifact

```bash
python simulate.py inspect report_20260421_120000_world.json --section leaders
```

Available sections:

- `summary`
- `leaders`
- `events`
- `conversations`
- `agents`
- `all`

### Search an artifact

```bash
python simulate.py search report_20260421_120000_world.json tariffs
```

### Ask questions about an artifact

```bash
python simulate.py ask report_20260421_120000_world.json "How did the grounded leaders react?"
```

## How The System Works

1. Build or reconstruct the world state.
2. Calibrate the simulated population to that baseline.
3. Ground named real-world actors when the scenario warrants it.
4. Parse the theory into initial events.
5. Simulate conversations, reactions, and emergent events over time.
6. Generate decision-facing outputs and persist the run as an artifact.

## Project Structure

```text
agents/        Archetype agents and world initialization
grounding/     Baseline reconstruction, live data, search, and leader grounding
simulation/    Core simulation engine, events, and artifact persistence
report/        Markdown report generation
presentation/  Slide deck and video-brief generation
landing/       Marketing site and deployment assets
simulate.py    Main CLI entrypoint
```

## Example Use Cases

- Test how export controls propagate through leaders, firms, and populations.
- Compare geopolitical or infrastructure shocks against the current global baseline.
- Generate a report and slide deck for a government or strategy lens.
- Save a world artifact and return later to inspect conversations, events, or leadership reactions.

## Current Limits

- Live grounding is only as good as the configured search provider and available source coverage.
- Named actor grounding is targeted at serious policy and geopolitical scenarios, not every prompt.
- The simulation is useful for structured scenario exploration, not for deterministic prediction.
- Presentation rendering requires Marp CLI if you want exported `pdf`, `pptx`, or `html` output.

## Landing Page

The repo also includes a standalone landing page in [`landing/`](./landing) and deploys it separately from the simulation CLI.
