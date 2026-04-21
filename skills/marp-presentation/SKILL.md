---
name: marp-presentation
description: Use when creating deterministic Marp slide decks and rendering them with Marp CLI for this project. Prefer the project’s structured findings report, render with `marp` if installed or `npx @marp-team/marp-cli@latest` otherwise, and always provide the exact fallback command if rendering fails.
---

# Marp Presentation

Use this skill for presentation outputs in this repository.

## Workflow

1. Generate the findings report first.
2. Build slides deterministically from ranked findings, unexpected outcomes, trajectories, and top cascades.
3. Render with Marp CLI:
   - Prefer `marp <deck> --pdf -o <out>` when a global `marp` binary exists.
   - Otherwise use `npx @marp-team/marp-cli@latest <deck> --pdf -o <out>`.
4. If rendering fails, always return the exact command for the user to run manually.

## Rules

- Keep decks concise: 8-12 slides.
- Avoid LLM-written filler prose when deterministic findings already exist.
- Prefer bullet-driven slides over paragraph-heavy slides.
- Use the project’s strongest visual assets:
  - current world state snapshot
  - top findings
  - unexpected outcomes
  - butterfly-effect cascades
- If PDF export fails, also suggest `pptx` as fallback.

## Commands

PDF:

```bash
npx @marp-team/marp-cli@latest report_YYYYMMDD_HHMMSS_slides.md --pdf -o report_YYYYMMDD_HHMMSS_slides.pdf
```

PPTX:

```bash
npx @marp-team/marp-cli@latest report_YYYYMMDD_HHMMSS_slides.md --pptx -o report_YYYYMMDD_HHMMSS_slides.pptx
```
