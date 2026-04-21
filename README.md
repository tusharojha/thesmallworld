# The Small World

The Small World is a current-state-grounded forecasting engine for policy, market, infrastructure, and geopolitical shocks. It reconstructs a live baseline from source-backed indicators, simulates graph-based cascades across populations and institutions, and produces decision-grade outputs around propagation, concentration, volatility, and emergent risk.

## Positioning

- Product category: decision intelligence platform
- Core wedge: global policy and macro-shock forecasting
- Primary user: policy analyst, strategist, macro researcher, or infrastructure planner
- Competition direction: Challenge 04 style framing around global coordination and intelligent infrastructure

## What It Does

1. Reconstructs the current world state from country indicators and topic-sensitive discourse signals.
2. Calibrates a multi-country archetype population against that baseline.
3. Injects a shock such as tariffs, UBI, export controls, sanctions, energy spikes, or infrastructure failures.
4. Propagates direct and second-order effects through an explicit social graph.
5. Produces a decision brief, presentation deck, and optional video brief.

## Output Model

The system is being shaped toward four competition-facing outputs:

- Current world state reconstruction with observed vs inferred signals and baseline confidence
- Shock propagation analysis with cascades, amplifiers, bridge nodes, and absorber populations
- System stress map showing geography concentration and volatility
- Leading indicators and decision-maker framing for intervention design

## CLI

```bash
python simulate.py \
  --theory "A major semiconductor export restriction is introduced" \
  --grounding live \
  --search-provider searxng \
  --steps 8 \
  --lens government \
  --presentation
```

Useful options:

- `--grounding live` to reconstruct the current baseline before simulation
- `--search-provider brave|searxng` to add live discourse pulse inference
- `--lens government|central-bank|ngo|enterprise-strategy` to frame outputs for a decision-maker
- `--presentation` to generate a Marp deck
- `--video-brief` to generate a production brief for downstream video workflows

## Near-Term Competition Work

- Make the current world state dashboard a first-class product surface
- Add explicit baseline vs scenario vs alternative scenario comparison
- Add richer shock propagation visualization beyond terminal output
- Add cascade confidence scoring and ranked emergent outcomes
- Polish one flagship demo around a serious macro or geopolitical event
