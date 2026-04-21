// Data for The Small World — grounded in current-world-state reconstruction

window.TSW_DATA = {
  suggestions: [
    "A major semiconductor export restriction is introduced",
    "UBI is piloted across three G7 economies",
    "The Strait of Hormuz closes for 72 hours",
    "The EU agrees a carbon-border levy overnight",
    "Sanctions on a top-5 oil exporter tighten",
    "A severe drought cuts Panama Canal transits by half"
  ],

  agentNames: [
    { n: "LEADER · US_EXEC",       s: "thinking" },
    { n: "LEADER · PBOC",          s: "thinking" },
    { n: "MINISTRY · METI_JP",     s: "ready"   },
    { n: "POP · MANUFACTURING_DE", s: "ready"   },
    { n: "POP · HOUSEHOLD_IN",     s: "idle"    },
    { n: "FIRM · CHIP_FAB_TW",     s: "thinking"},
    { n: "FIRM · LOGISTICS_NL",    s: "ready"   },
    { n: "INST · ECB",             s: "thinking"},
    { n: "INST · IMF",             s: "ready"   },
    { n: "POP · LABOR_BR",         s: "idle"    },
    { n: "MEDIA · WIRE_EN",        s: "ready"   },
    { n: "POP · RETAIL_US",        s: "idle"    },
  ],

  // The five-stage loop, mapped to the real pipeline
  loopStages: [
    { idx: "01", t: "Ground",    desc: "Current world state is reconstructed from country indicators and topic-sensitive discourse. Observed vs. inferred signals are labeled." },
    { idx: "02", t: "Calibrate", desc: "A multi-country archetype population is fit to the baseline. Named leaders and institutions are grounded as explicit actors." },
    { idx: "03", t: "Shock",     desc: "A tariff, export control, UBI pilot, sanction, or infrastructure failure is injected into the social graph." },
    { idx: "04", t: "Propagate", desc: "Cascades traverse explicit edges. Amplifiers, bridge nodes, and absorber populations emerge — sometimes uncomfortably." },
    { idx: "05", t: "Brief",     desc: "A decision brief, deck, and optional video are produced. A queryable world artifact is saved for follow-up questions." },
  ],

  // Agent graph — grounded leaders + institutions + archetype populations + firms
  agents: [
    { id: "useexec", label: "US EXECUTIVE",   sub: "GROUNDED · LEADER",   role: "Grounded leader",    x: 0.48, y: 0.18, color: "var(--crimson)",
      beliefs: "Protect domestic fabs; price in electoral cost of consumer-facing tariffs; signal resolve to allies.",
      quote: "We will calibrate, but we will not concede the advantage.",
      deg: { in: 21, out: 34 } },
    { id: "pboc",    label: "PBOC",           sub: "GROUNDED · CENTRAL BANK", role: "Grounded institution", x: 0.82, y: 0.22, color: "var(--crimson)",
      beliefs: "Defend the currency corridor; front-run retaliation with liquidity; industrial policy footprint widens.",
      quote: "We have instruments. We prefer not to explain them.",
      deg: { in: 14, out: 22 } },
    { id: "fab",     label: "CHIP FAB",       sub: "FIRM · HSINCHU",      role: "Firm archetype",     x: 0.72, y: 0.50, color: "var(--ocean)",
      beliefs: "Reprice capex; diversify customers; hedge equipment-license exposure within 60 days.",
      quote: "We cannot be both indispensable and neutral indefinitely.",
      deg: { in: 11, out: 18 } },
    { id: "metijp",  label: "METI",           sub: "GROUNDED · MINISTRY", role: "Grounded institution", x: 0.26, y: 0.28, color: "var(--crimson)",
      beliefs: "Align materials export policy with allied posture; subsidize domestic equivalents; protect bilateral access.",
      quote: "We are adjacent to the problem. We intend to stay adjacent.",
      deg: { in: 9, out: 14 } },
    { id: "mfgde",   label: "MANUFACTURING",  sub: "POPULATION · DE",     role: "Archetype pop.",     x: 0.16, y: 0.56, color: "var(--forest)",
      beliefs: "Order book intact; component substitution stressful; layoffs pushed into Q3.",
      quote: "We can absorb one shock. We have already absorbed three.",
      deg: { in: 8, out: 6 } },
    { id: "housein", label: "HOUSEHOLD",      sub: "POPULATION · IN",     role: "Archetype pop.",     x: 0.40, y: 0.78, color: "var(--forest)",
      beliefs: "Inflation sensitive; staples first; durables deferred until monsoon is priced.",
      quote: "The news is loud. The receipt is louder.",
      deg: { in: 7, out: 3 } },
    { id: "retailus",label: "RETAIL",         sub: "POPULATION · US",     role: "Archetype pop.",     x: 0.62, y: 0.78, color: "var(--forest)",
      beliefs: "Back-to-school pricing binds first; swap to private label; political attribution is partisan.",
      quote: "We do not read press releases. We read shelves.",
      deg: { in: 6, out: 4 } },
    { id: "wire",    label: "WIRE / EN",      sub: "DISCOURSE · MEDIA",   role: "Narrator",           x: 0.50, y: 0.48, color: "var(--ochre)",
      beliefs: "Amplifies resolved consensus; undercovers absorbers; overcovers bridge nodes.",
      quote: "We write what the market has already decided to believe.",
      deg: { in: 28, out: 46 } },
    { id: "imf",     label: "IMF",            sub: "GROUNDED · INSTITUTION", role: "Grounded institution", x: 0.86, y: 0.62, color: "var(--crimson)",
      beliefs: "Conditional support to exposed EMs; coordinate with regional banks; flag contagion to deficit economies.",
      quote: "We can arrive quickly. Arriving is not the hard part.",
      deg: { in: 10, out: 13 } },
  ],

  edges: [
    ["useexec","pboc"], ["useexec","metijp"], ["useexec","fab"], ["useexec","wire"],
    ["pboc","fab"], ["pboc","imf"], ["pboc","wire"],
    ["metijp","fab"], ["metijp","mfgde"],
    ["fab","mfgde"], ["fab","retailus"], ["fab","wire"],
    ["mfgde","housein"], ["mfgde","wire"],
    ["wire","retailus"], ["wire","housein"], ["wire","imf"],
    ["imf","housein"], ["imf","retailus"]
  ],

  // Four flagship runs — chosen to match the real product's intended use
  theories: [
    {
      tag: "trading", tagLabel: "§ 3.1 · MACRO SHOCK",
      title: "\u201CA major semiconductor export restriction is introduced.\u201D",
      summary: "Grounded against current leaders and institutions. 412 archetype agents across 9 economies. Cascade traced through 6 bridge nodes; two absorbers identified.",
      conf: "0.64", pop: "Lens · government",
    },
    {
      tag: "geo", tagLabel: "§ 3.2 · POLICY",
      title: "\u201CUBI is piloted across three G7 economies, simultaneously.\u201D",
      summary: "Baseline reconstructed from labor, fiscal, and discourse indicators. Population archetypes re-fit. Second-order labor-force effects diverge sharply by country.",
      conf: "0.52", pop: "Lens · central-bank",
    },
    {
      tag: "science", tagLabel: "§ 3.3 · INFRASTRUCTURE",
      title: "\u201CA severe drought cuts Panama Canal transits by half for a year.\u201D",
      summary: "Logistics firms, shippers, and downstream retailers re-route. Discourse pulse shifts on week 3. Concentration risk found where nobody was looking.",
      conf: "0.71", pop: "Lens · enterprise-strategy",
    },
    {
      tag: "whatif", tagLabel: "§ 3.4 · COUNTERFACTUAL",
      title: "\u201CThe EU agrees a carbon-border levy, overnight, without warning.\u201D",
      summary: "Grounded leadership dossiers used. Retaliation sequence simulated across 14 rounds. Absorber populations identified — not the ones the memos assumed.",
      conf: "0.58", pop: "Lens · ngo",
    },
  ],

  // Four flagship output types, exactly as shaped in the roadmap
  useCases: [
    { v: "Current-state reconstruction", desc: "The baseline the scenario will be measured against. Observed signals labeled; inferred signals confidence-scored. Live if a search provider is configured.", artifact: "Output 01 · World brief" },
    { v: "Shock propagation analysis",   desc: "Cascades across the explicit social graph. Amplifiers, bridge nodes, and absorbers named. The second-order effects that nobody asked you to consider.",   artifact: "Output 02 · Cascade map" },
    { v: "System stress map",            desc: "Geographic concentration and volatility surfaces. Where the system is thin, and where the system is pretending to be thick.",                              artifact: "Output 03 · Stress atlas" },
    { v: "Decision framing",             desc: "Leading indicators and intervention design, framed for a specific lens: government, central bank, NGO, enterprise strategy. A brief you can staff against.", artifact: "Output 04 · Decision brief" },
    { v: "Queryable world artifact",     desc: "The whole run, saved. Inspect leaders, search conversations, ask higher-level questions later, without rebuilding the scenario.",                              artifact: "Output 05 · World artifact" },
  ],

  faqs: [
    { q: "What makes this different from a scenario memo or a Monte Carlo?",
      a: "Memos argue. Monte Carlo samples a distribution. The Small World reconstructs a current-world-state baseline, populates it with archetype agents plus grounded leaders and institutions, and propagates a shock through an explicit social graph. The distribution is an emergent property of deliberation, not an input." },
    { q: "What does 'grounded' mean, exactly?",
      a: "For serious international scenarios with a search provider configured, we attempt to ground named leadership and institutional actors: who is in office now, which institution they represent, what constraints they face, and what posture they currently signal. These dossiers are added as explicit nodes in the world." },
    { q: "What comes out of a run?",
      a: "Four decision-grade outputs: a current-state reconstruction, a shock-propagation analysis, a system stress map, and a decision brief framed for your chosen lens. Optional: a Marp deck, a video brief, and a queryable world artifact you can inspect, search, and ask questions against later." },
    { q: "How do I run one?",
      a: "The CLI: python simulate.py run --theory \"…\" --grounding live --steps 8 --lens government --presentation. Swap lens for central-bank, ngo, or enterprise-strategy. Add --named-actors auto for grounded leaders on policy or geopolitical scenarios." },
    { q: "How long does a run take, and what does it cost?",
      a: "A grounded 8-step policy run resolves in 25–60 minutes of real time. Without live grounding, considerably less. Cost scales with agent count, step count, and whether discourse pulse inference is enabled." },
    { q: "Can I trust the output?",
      a: "Trust the disagreements. The brief surfaces where agents converged, where they split, and where confidence is thin. A strong consensus with a loud absorber population is often more actionable than a weak consensus with no friction." },
    { q: "Is my scenario visible to other users?",
      a: "No. Theories, transcripts, and world artifacts are yours. Institutional runs can be air-gapped; the repo is open-source, so you can run the whole thing behind your own perimeter." },
    { q: "Where does this go next?",
      a: "A first-class current-world-state dashboard, explicit baseline-vs-scenario-vs-alt-scenario comparison, richer cascade visualization beyond the terminal, cascade confidence scoring, and one flagship macro demo we keep sharpening until it draws blood." },
  ],
};
