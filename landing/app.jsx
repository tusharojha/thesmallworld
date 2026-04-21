// The Small World — landing page
const { useState, useEffect, useRef, useMemo } = React;

const D = window.TSW_DATA;

// ============ CLI HERO (static recreation of terminal TUI) ============
function CliHero() {
  const agents = [
    { n: "Representa", cc: "US", m: "hopeful",     s: "ok" },
    { n: "Alexander",  cc: "US", m: "anxious",     s: "anxious" },
    { n: "Tucker_ana", cc: "US", m: "anxious",     s: "anxious" },
    { n: "Senator_Mor",cc: "US", m: "determined",  s: "determined" },
    { n: "Nadia",      cc: "UK", m: "hopeful",     s: "ok" },
    { n: "Anika",      cc: "IN", m: "hopeful",     s: "ok" },
    { n: "Tariq",      cc: "US", m: "hopeful",     s: "ok" },
    { n: "Katya",      cc: "RU", m: "hopeful",     s: "ok" },
    { n: "Sarah",      cc: "AU", m: "anxious",     s: "anxious" },
    { n: "Liam",       cc: "CA", m: "hopeful",     s: "ok" },
    { n: "Erik",       cc: "SE", m: "hopeful",     s: "ok" },
    { n: "Jisoo",      cc: "KR", m: "anxious",     s: "anxious" },
    { n: "Astrid",     cc: "NO", m: "hopeful",     s: "ok" },
    { n: "Hiroshi",    cc: "JP", m: "hopeful",     s: "ok" },
    { n: "Nong",       cc: "TH", m: "hopeful",     s: "ok" },
    { n: "Kwame",      cc: "GH", m: "hopeful",     s: "ok" },
    { n: "Emeka",      cc: "NG", m: "anxious",     s: "anxious" },
    { n: "Mei",        cc: "CN", m: "hopeful",     s: "ok" },
    { n: "Amara",      cc: "ET", m: "hopeful",     s: "ok" },
    { n: "Diego",      cc: "MX", m: "hopeful",     s: "ok" },
  ];

  const econ = [
    { c: "Poland",  v: 0.70, hi: true },
    { c: "South",   v: 0.70, hi: true },
    { c: "Nigeria", v: 0.55 },
    { c: "China",   v: 0.53 },
    { c: "Brazil",  v: 0.51 },
    { c: "India",   v: 0.45 },
    { c: "France",  v: 0.45 },
  ];

  const beliefs = [
    { l: "Emergence of coalitions", v: "+0.90" },
    { l: "Advocacy grows",          v: "+0.89" },
    { l: "Global issue momentum",   v: "+0.89" },
    { l: "Gender-equity gain",      v: "+0.89" },
    { l: "Local advocacy",          v: "+0.81" },
    { l: "Public trust",            v: "+0.79" },
  ];

  const events = [
    "Wk 2 · International Relations",
    "Wk 3 · Local Advocacy Group",
    "Wk 3 · Community Town Hall",
    "Wk 3 · Public Sentiment on…",
  ];

  return (
    <section className="cli-hero">
      <div className="prompt">
        <span className="caret"></span>
        <span>The product is a CLI. The world is a terminal.</span>
      </div>

      <div className="cli-window">
        <div className="cli-titlebar">
          <div className="dots"><span></span><span></span><span></span></div>
          <div className="t">thesmallworld — simulate.py run --theory "…" --grounding live</div>
          <div>TMUX · 0</div>
        </div>
        <div className="cli-topbar">
          <div className="brand">THE SMALL WORLD</div>
          <div className="theory">"What would 2026 look like if the world was ruled by women leaders?"</div>
          <div className="tick">Week 4/4 · 01:57</div>
        </div>

        <div className="cli-grid">
          {/* AGENTS */}
          <div className="cli-col">
            <div className="hdr"><span>AGENTS</span><span className="meta">51 / 51</span></div>
            {agents.map((a, i) => (
              <div key={i} className="cli-agent">
                <span className={`dot ${a.s}`}>●</span>
                <span className="n">{a.n}</span>
                <span className="cc">{a.cc}</span>
                <span className={`m ${a.s}`}>{a.m}</span>
              </div>
            ))}
          </div>

          {/* LIVE FEED */}
          <div className="cli-col cli-feed">
            <div className="hdr"><span>LIVE FEED · WEEK 4</span><span className="meta">9 EMERGENT EVENTS</span></div>
            <div className="conv">
              <div className="pair">Tariq × Sofia</div>
              <div className="line"><b>Sofia:</b> I have! It's encouraging to see some progress.</div>
              <div className="line"><b>Tariq:</b> Yeah, I get that. Trusting institutions is…</div>
            </div>
            <div className="conv">
              <div className="pair">Kwame × Darnell</div>
              <div className="line"><b>Kwame:</b> I share that concern. My trust in institutions…</div>
              <div className="line"><b>Darnell:</b> Absolutely! If we unite voices from…</div>
            </div>
            <div className="conv">
              <div className="pair">Tucker_analog × Tyler</div>
              <div className="line"><b>Tyler:</b> I get that, Tucker, but I see a lot of potential…</div>
              <div className="line"><b>Tucker:</b> Diplomacy? With countries that don't share our…</div>
            </div>
            <div className="conv">
              <div className="pair">Sofia × Darnell</div>
              <div className="line"><b>Darnell:</b> Yeah, I've noticed. It's pretty overwhelming…</div>
              <div className="line"><b>Sofia:</b> Absolutely. It's like the decisions made by…</div>
            </div>
            <div className="conv">
              <div className="pair">Sofia × Tyler</div>
              <div className="line"><b>Sofia:</b> Hey Tyler, I've been reading a lot about how…</div>
              <div className="line"><b>Tyler:</b> Absolutely, Sofia! With everything going on globally…</div>
            </div>
            <div className="line em">…41 more conversations this week. 9 marked emergent.</div>
          </div>

          {/* WORLD STATE */}
          <div className="cli-col cli-world">
            <div className="hdr"><span>WORLD STATE</span></div>

            <div className="wsec">
              <h6>Polarization</h6>
              <div className="stat">
                <span className="lbl">index</span>
                <span className="bar"><span className="fl" style={{width: "41%"}}></span></span>
                <span className="v">0.41</span>
              </div>
            </div>

            <div className="wsec">
              <h6>Econ stress</h6>
              {econ.map((e, i) => (
                <div key={i} className="stat">
                  <span className="lbl">{e.c}</span>
                  <span className="bar"><span className={`fl ${e.hi ? "hi" : ""}`} style={{width: `${e.v*100}%`}}></span></span>
                  <span className="v">{e.v.toFixed(2)}</span>
                </div>
              ))}
            </div>

            <div className="wsec">
              <h6>Beliefs</h6>
              {beliefs.map((b, i) => (
                <div key={i} className="belief">
                  <span className="lbl">{b.l}</span>
                  <span className="v">{b.v}</span>
                </div>
              ))}
            </div>

            <div className="wsec">
              <h6>Events</h6>
              {events.map((e, i) => (
                <div key={i} className="event">{e}</div>
              ))}
            </div>
          </div>
        </div>

        <div className="cli-footer">
          <div className="cli-progress">
            <span className="p-lbl">Overall</span>
            <span className="p-bar"><span className="fl" style={{width: "100%"}}></span></span>
            <span className="p-val">Wk 4/4</span>
            <span className="p-lbl">Agents</span>
            <span className="p-bar"><span className="fl" style={{width: "100%"}}></span></span>
            <span className="p-val">51/51</span>
          </div>
          <div className="cli-statuses">
            <span>Elapsed <b>01:57</b></span>
            <span>Emergent <b>9</b></span>
            <span>Model <b>gpt-4o-mini</b></span>
            <span>Concurrency <b>20</b></span>
          </div>
        </div>
      </div>

      <div className="cli-invoke">
        <code>
          <span style={{color:"var(--ink-mute)"}}>$</span> python simulate.py run{" "}
          <span className="flag">--theory</span> <span className="str">"A semiconductor export restriction is introduced"</span>{" "}
          <span className="flag">--grounding</span> <span className="val">live</span>{" "}
          <span className="flag">--lens</span> <span className="val">government</span>{" "}
          <span className="flag">--steps</span> <span className="val">8</span>
        </code>
        <a className="cta" href="https://github.com/tusharojha/thesmallworld" target="_blank" rel="noopener">
          Clone & run ↗
        </a>
      </div>
    </section>
  );
}

// ============ DEMO VIDEO ============
function DemoVideo({ url }) {
  const [playing, setPlaying] = useState(false);
  // Parse YT id if provided, else placeholder
  const idMatch = url && url.match(/(?:v=|youtu\.be\/|embed\/)([A-Za-z0-9_-]{11})/);
  const ytId = idMatch ? idMatch[1] : null;

  return (
    <section className="paper" id="demo" style={{paddingTop:"64px"}}>
      <div className="sec-head">
        <div className="sec-num">§ 00<b>Demo</b></div>
        <div>
          <h2 className="sec-title">Three minutes of the <em>world</em>, running.</h2>
          <p className="sec-kicker">A narrated walk-through of a grounded run, from theory to decision brief.</p>
        </div>
      </div>
      <div className="body-col">
        <div className="side">
          <p><b>Run</b> · women-led 2026 counterfactual</p>
          <p><b>Agents</b> · 51</p>
          <p><b>Elapsed</b> · 01:57</p>
          <p><b>Model</b> · gpt-4o-mini</p>
        </div>
        <div className="main">
          <figure className="fig" style={{margin:0}}>
            <div className="demo-video">
              {playing && ytId ? (
                <iframe src={`https://www.youtube.com/embed/${ytId}?autoplay=1&rel=0`} allow="autoplay; encrypted-media; picture-in-picture" allowFullScreen></iframe>
              ) : (
                <div className="ph" onClick={() => ytId && setPlaying(true)}>
                  <div className="meta-overlay">▎ DEMO · 03:12 · YOUTUBE</div>
                  <div className="ring"><div className="tri"></div></div>
                  <div className="caption-overlay">“What would 2026 look like if the world was ruled by women leaders?” — a 51-agent run.</div>
                </div>
              )}
            </div>
            <figcaption className="cap">
              <span><b>Fig. 0</b>{ytId ? "Click to play the demo." : "Demo video."}</span>
              <span>YouTube</span>
            </figcaption>
          </figure>
        </div>
      </div>
    </section>
  );
}

// ============ §1 HOW IT WORKS ============
function LoopDiagram() {
  const [active, setActive] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setActive((a) => (a + 1) % D.loopStages.length), 2400);
    return () => clearInterval(id);
  }, []);

  return (
    <section className="paper" id="method">
      <div className="sec-head">
        <div className="sec-num">§ 01<b>Method</b></div>
        <div>
          <h2 className="sec-title">Reconstruct. Inject. <em>Propagate</em>.</h2>
          <p className="sec-kicker">Five stages, grounded against current indicators. Not a distribution — a deliberation.</p>
        </div>
      </div>

      <div className="body-col">
        <div className="side">
          <p><b>§ 1.1</b> Source-backed baseline.</p>
          <p><b>§ 1.2</b> Grounded leaders.</p>
          <p><b>§ 1.3</b> Explicit edges.</p>
          <p><b>§ 1.4</b> Decision-grade outputs.</p>
        </div>
        <div className="main">
          <p>A shock arrives in plain language. The platform reconstructs the <span className="ocean">current world state</span> from country indicators and discourse, then calibrates archetype populations against it. For serious scenarios, named leaders are grounded as explicit nodes. Then the shock propagates — and the absorbers are usually not the ones the memo assumed.</p>

          <figure className="fig">
            <div className="loop-diagram">
              <div className="loop-stages">
                {D.loopStages.map((s, i) => (
                  <div
                    key={s.idx}
                    className={`loop-stage ${i === active ? "active" : ""}`}
                    onClick={() => setActive(i)}
                    onMouseEnter={() => setActive(i)}
                  >
                    <div className="tick"></div>
                    <div className="idx"><b>{s.idx}</b>stage</div>
                    <h4>{s.t}</h4>
                    <p>{s.desc}</p>
                  </div>
                ))}
              </div>
              <div className="loop-arrow">
                <span>Each stage writes to the next. The artifact persists. <span className="curve">↻</span></span>
              </div>
            </div>
            <figcaption className="cap">
              <span><b>Fig. 1</b>The pipeline. Hover to pause.</span>
              <span>n = 5 stages</span>
            </figcaption>
          </figure>
        </div>
      </div>
    </section>
  );
}

// ============ §2 AGENT GRAPH ============
function AgentGraph() {
  const [sel, setSel] = useState(D.agents[0]);
  const [pulse, setPulse] = useState(0);
  const svgRef = useRef(null);
  const W = 1100, H = 520;

  useEffect(() => {
    const id = setInterval(() => setPulse((p) => p + 1), 1200);
    return () => clearInterval(id);
  }, []);

  const agentById = useMemo(() => Object.fromEntries(D.agents.map((a) => [a.id, a])), []);
  const pos = (a) => ({ x: a.x * W, y: a.y * H });

  return (
    <section className="paper" id="agents">
      <div className="sec-head">
        <div className="sec-num">§ 02<b>Architecture</b></div>
        <div>
          <h2 className="sec-title">Grounded leaders, institutions, and archetype <em>populations</em> on one graph.</h2>
          <p className="sec-kicker">Click any node.</p>
        </div>
      </div>

      <div className="body-col">
        <div className="side">
          <p><b>Crimson</b> nodes are grounded from live search.</p>
          <p><b>Green</b> nodes are calibrated populations.</p>
          <p><b>Size</b> is reach in the cascade.</p>
        </div>
        <div className="main">
          <figure className="fig">
            <div className="agent-graph">
              <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet">
                {D.edges.map(([a, b], i) => {
                  const A = pos(agentById[a]), B = pos(agentById[b]);
                  const isActive = (pulse + i) % 5 === 0 || sel.id === a || sel.id === b;
                  return (
                    <line key={i}
                      x1={A.x} y1={A.y} x2={B.x} y2={B.y}
                      className={`agent-edge ${isActive ? "active" : ""}`}
                      strokeDasharray={isActive ? "4 3" : "none"}
                    />
                  );
                })}
                {D.agents.map((a) => {
                  const p = pos(a);
                  const r = 10 + (a.deg.in + a.deg.out) * 0.35;
                  const isSel = sel.id === a.id;
                  return (
                    <g key={a.id} className={`agent-node ${isSel ? "selected" : ""}`}
                       transform={`translate(${p.x}, ${p.y})`}
                       onClick={() => setSel(a)}>
                      <circle r={r + 6} fill="var(--paper)" opacity="0.9" />
                      <circle r={r} fill={isSel ? "var(--paper)" : a.color}
                              stroke={a.color} strokeWidth={isSel ? 2.5 : 1.2} />
                      {isSel && <circle r={r + 3} fill="none" stroke="var(--ink)" strokeDasharray="2 3"/>}
                      <text y={-r - 10} textAnchor="middle" className="agent-label">{a.label}</text>
                      <text y={-r - 22} textAnchor="middle" className="agent-sub">{a.sub}</text>
                    </g>
                  );
                })}
              </svg>

              <div className="agent-detail">
                <div className="role">{sel.role}</div>
                <h5>{sel.label}</h5>
                <div className="stats">
                  <div className="row">IN<b>{sel.deg.in}</b></div>
                  <div className="row">OUT<b>{sel.deg.out}</b></div>
                </div>
                <div style={{fontSize:"11px", fontFamily:"var(--mono)", color:"var(--ink-mute)", letterSpacing:"0.1em", textTransform:"uppercase", marginBottom:"8px"}}>Posture</div>
                <p style={{margin:"0 0 14px", fontSize:"14px", color:"var(--ink-soft)", lineHeight:1.5}}>{sel.beliefs}</p>
                <div className="quote">{sel.quote}</div>
              </div>

              <div className="graph-legend">
                <div className="row"><span className="sw" style={{background:"var(--crimson)"}}></span>Grounded</div>
                <div className="row"><span className="sw" style={{background:"var(--forest)"}}></span>Population</div>
                <div className="row"><span className="sw" style={{background:"var(--ocean)"}}></span>Firm</div>
                <div className="row"><span className="sw" style={{background:"var(--ochre)"}}></span>Discourse</div>
              </div>
            </div>
            <figcaption className="cap">
              <span><b>Fig. 2</b>Actor graph fragment. Click any node.</span>
              <span>n = 9 of 412</span>
            </figcaption>
          </figure>
        </div>
      </div>
    </section>
  );
}

// ============ §3 EXAMPLE THEORIES ============
function Theories() {
  return (
    <section className="paper" id="theories">
      <div className="sec-head">
        <div className="sec-num">§ 03<b>Selected runs</b></div>
        <div>
          <h2 className="sec-title">Four shocks. Four <em>lenses</em>.</h2>
          <p className="sec-kicker">Each one groundable against live indicators.</p>
        </div>
      </div>

      <div className="theories">
        {D.theories.map((t, i) => (
          <div key={i} className="theory-card">
            <div className={`tag ${t.tag}`}>
              <span className="d"></span>{t.tagLabel}
            </div>
            <h4>{t.title}</h4>
            <p className="summary">{t.summary}</p>
            <div className="footer">
              <span className="conf">Confidence <b>{t.conf}</b></span>
              <span>{t.pop}</span>
              <span className="go">Read brief →</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

// ============ §4 SAMPLE REPORT ============
function ReportPreview() {
  const [pos, setPos] = useState(72);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    if (!playing) return;
    const id = setInterval(() => {
      setPos((p) => {
        if (p >= 100) { setPlaying(false); return 100; }
        return p + 1;
      });
    }, 120);
    return () => clearInterval(id);
  }, [playing]);

  const n = 60;
  const seed = 19;
  const chartPath = useMemo(() => {
    const pts = [];
    for (let i = 0; i < n; i++) {
      const x = (i / (n - 1)) * 100;
      const t = i / n;
      const trend = 42 + t * 28;
      const wobble = Math.sin(i * 0.62 + seed) * 5 + Math.sin(i * 0.21) * 3;
      const shock = i > 18 ? Math.min(22, (i - 18) * 1.8) : 0;
      const y = trend + wobble + shock;
      pts.push([x, y]);
    }
    return pts.map((p, i) => `${i === 0 ? "M" : "L"}${p[0]},${p[1]}`).join(" ");
  }, []);
  const bandUpper = useMemo(() => {
    const pts = [];
    for (let i = 0; i < n; i++) {
      const x = (i / (n - 1)) * 100;
      const t = i / n;
      const shock = i > 18 ? Math.min(22, (i - 18) * 1.8) : 0;
      pts.push([x, 32 + t * 22 + shock - 6]);
    }
    return pts.map((p, i) => `${i === 0 ? "M" : "L"}${p[0]},${p[1]}`).join(" ");
  }, []);
  const bandLower = useMemo(() => {
    const pts = [];
    for (let i = 0; i < n; i++) {
      const x = (i / (n - 1)) * 100;
      const t = i / n;
      const shock = i > 18 ? Math.min(22, (i - 18) * 1.8) : 0;
      pts.push([x, 58 + t * 28 + shock + 6]);
    }
    return pts.map((p, i) => `${i === 0 ? "M" : "L"}${p[0]},${p[1]}`).join(" ");
  }, []);

  return (
    <section className="paper" id="report">
      <div className="sec-head">
        <div className="sec-num">§ 04<b>Output</b></div>
        <div>
          <h2 className="sec-title">A decision brief a <em>colleague</em> would write.</h2>
          <p className="sec-kicker">Citable, footnoted, and honest about where the actors disagreed.</p>
        </div>
      </div>

      <div className="report">
        <div className="rhead">
          <span>Run 0x7A·4F12 · lens: government · 412 actors</span>
          <span>Grounded · 41m 28s</span>
        </div>
        <h3 className="rtitle">On the Propagation of a Semiconductor Export Restriction</h3>
        <p className="rsub">A grounded baseline, a six-hop cascade, and two absorbers the memos missed.</p>

        <div className="summary-grid">
          <div className="cell"><div className="lbl">Baseline conf.</div><div className="val pos">0.78</div></div>
          <div className="cell"><div className="lbl">Cascade depth</div><div className="val neu">6 hops</div></div>
          <div className="cell"><div className="lbl">Stress index</div><div className="val neg">+0.42</div></div>
          <div className="cell"><div className="lbl">Dissent</div><div className="val neu">0.31</div></div>
        </div>

        <h4 className="rh">Finding</h4>
        <p className="rp">
          The shock is priced as <span className="hl">coordinated, not unilateral</span> within 72 simulated hours.
          The <span className="hl">PBOC</span> front-runs retaliation with liquidity<sup>1</sup>. The absorbers are
          German manufacturing and Indian households<sup>2</sup> — not the fabs.
        </p>

        <h4 className="rh">Cascade path · median of 240 runs</h4>
        <div className="chart">
          <div className="cap">STRESS INDEX · NORMALIZED</div>
          <svg viewBox="0 0 100 100" preserveAspectRatio="none">
            <path d={`${bandUpper} L 100,100 L 0,100 Z`} fill="rgba(139,58,58,0.06)"/>
            <path d={`${bandLower} L 100,100 L 0,100 Z`} fill="rgba(250,250,247,1)"/>
            <path d={chartPath} stroke="var(--crimson)" strokeWidth="0.6" fill="none" vectorEffect="non-scaling-stroke"/>
            <line x1="30" x2="30" y1="0" y2="100" stroke="var(--ink)" strokeWidth="0.3" strokeDasharray="1.5 2" vectorEffect="non-scaling-stroke" opacity="0.5"/>
            <text x="31" y="10" fontSize="3" fill="var(--ink-mute)" fontFamily="var(--mono)">SHOCK · T+0</text>
            <line x1={pos} x2={pos} y1="0" y2="100" stroke="var(--ink)" strokeWidth="0.4" vectorEffect="non-scaling-stroke" strokeDasharray="2 2"/>
            <circle cx={pos} cy={50} r="1.2" fill="var(--ochre)"/>
          </svg>
        </div>

        <h4 className="rh">Leading indicators</h4>
        <p className="rp">
          Watch the <span className="hl">equipment-license register</span> at week 2 and <span className="hl">chip-fab capex guidance</span> at week 5<sup>3</sup>.
          Both move before the narrative resolves.
        </p>

        <div className="refs">
          <div className="r"><span className="n">[1]</span><span>Grounded dossier · PBOC · rounds 14–42.</span></div>
          <div className="r"><span className="n">[2]</span><span>Archetypes · MANUFACTURING_DE, HOUSEHOLD_IN · welfare −1.8% / −0.9%.</span></div>
          <div className="r"><span className="n">[3]</span><span>Discourse pulse · searxng · entropy 0.44.</span></div>
        </div>
      </div>

      <div className="report-controls">
        <button onClick={() => setPlaying(!playing)}>{playing ? "Pause" : "Scrub"} ▶</button>
        <div className="scrub">
          <span>T+0</span>
          <div className="track" onClick={(e) => {
            const r = e.currentTarget.getBoundingClientRect();
            setPos(((e.clientX - r.left) / r.width) * 100);
          }}>
            <div className="fill" style={{ width: `${pos}%` }}></div>
            <div className="knob" style={{ left: `${pos}%` }}></div>
          </div>
          <span>T+8</span>
        </div>
        <button onClick={() => { setPos(0); setPlaying(true); }}>Replay ↺</button>
      </div>
    </section>
  );
}

// ============ §5 USE CASES ============
function UseCases() {
  return (
    <section className="paper" id="applications">
      <div className="sec-head">
        <div className="sec-num">§ 05<b>Outputs</b></div>
        <div>
          <h2 className="sec-title">Five artifacts per run.</h2>
          <p className="sec-kicker">Propagation, concentration, volatility, emergent risk.</p>
        </div>
      </div>

      <div className="uc-table">
        {D.useCases.map((u, i) => (
          <div key={i} className="uc-row">
            <div className="idx">§ 5.{i + 1}</div>
            <div className="vert"><em>{u.v.split(" ")[0]}</em> {u.v.split(" ").slice(1).join(" ")}</div>
            <div className="desc">{u.desc}</div>
            <div className="artifact">{u.artifact}</div>
          </div>
        ))}
      </div>

      <div style={{
        marginTop:"48px", display:"grid", gridTemplateColumns:"180px 1fr", gap:"40px"
      }}>
        <div style={{fontFamily:"var(--mono)", fontSize:"11px", letterSpacing:"0.14em", textTransform:"uppercase", color:"var(--ink-mute)", paddingTop:"8px"}}>
          § 5.6 · Artifact
        </div>
        <div style={{border:"1px solid var(--ink)", background:"#0f1419", color:"#d8d2c0",
            fontFamily:"var(--mono)", fontSize:"13px", lineHeight:1.65, padding:"22px 24px"}}>
          <div style={{fontSize:"10px", letterSpacing:"0.14em", color:"#6b6a63", marginBottom:"14px"}}>CHAT WITH THE WORLD · AFTER THE RUN</div>
          <div><span style={{color:"#6b6a63"}}>$</span> simulate.py inspect report_world.json --section leaders</div>
          <div><span style={{color:"#6b6a63"}}>$</span> simulate.py search  report_world.json tariffs</div>
          <div><span style={{color:"#6b6a63"}}>$</span> simulate.py ask     report_world.json <span style={{color:"#c9a961"}}>"How did the grounded leaders react?"</span></div>
          <div style={{marginTop:"12px", color:"#8a8678", fontStyle:"italic"}}>→ Run once. Ask later.</div>
        </div>
      </div>
    </section>
  );
}

// ============ §6 FAQ ============
function FAQ() {
  const [open, setOpen] = useState(0);
  return (
    <section className="paper" id="questions">
      <div className="sec-head">
        <div className="sec-num">§ 06<b>Questions</b></div>
        <div>
          <h2 className="sec-title">Reviewer <em>№ 2</em>, addressed.</h2>
        </div>
      </div>

      <div className="faq-list">
        {D.faqs.map((f, i) => (
          <div key={i} className={`faq-item ${open === i ? "open" : ""}`} onClick={() => setOpen(open === i ? -1 : i)}>
            <div className="faq-q">
              <span className="n">§ 6.{i + 1}</span>
              <span className="t">{f.q}</span>
              <span className="x">+</span>
            </div>
            <div className="faq-a"><p>{f.a}</p></div>
          </div>
        ))}
      </div>
    </section>
  );
}

// ============ CTA + COLOPHON ============
function CTA() {
  return (
    <section className="cta-block">
      <h3>Stress-test the shock by <em>populating a world</em> and watching it push back.</h3>
      <p className="sub">Open-source. Runs locally. Bring your own search provider.</p>
      <div style={{display:"flex", gap:"14px", justifyContent:"center", flexWrap:"wrap"}}>
        <a className="cta-btn" href="https://github.com/tusharojha/thesmallworld" target="_blank" rel="noopener"
          style={{textDecoration:"none"}}>
          Clone the repo <span className="arr">↗</span>
        </a>
        <a className="cta-btn" href="#demo"
          style={{background:"transparent", color:"var(--ink)", border:"1px solid var(--ink)", textDecoration:"none"}}>
          Watch the demo <span className="arr">→</span>
        </a>
      </div>
    </section>
  );
}

function Colophon() {
  return (
    <div className="colophon">
      <div>
        <b>The Small World</b>
        <div>Vol. 1 · Issue 01 · April 2026</div>
        <div style={{marginTop:"8px"}}>Open-source.</div>
      </div>
      <div>
        <b>Sections</b>
        <a href="#demo">§ 00 · Demo</a>
        <a href="#method">§ 01 · Method</a>
        <a href="#agents">§ 02 · Architecture</a>
        <a href="#theories">§ 03 · Runs</a>
        <a href="#report">§ 04 · Output</a>
        <a href="#applications">§ 05 · Outputs</a>
      </div>
      <div>
        <b>Contact</b>
        <a href="https://github.com/tusharojha/thesmallworld" target="_blank" rel="noopener">github.com/tusharojha/thesmallworld</a>
        <a>Research affiliates</a>
        <a>Press</a>
      </div>
    </div>
  );
}

// ============ MASTHEAD + TITLE ============
// ORBIT logo mark — globe with agent dots on orbit
function OrbitMark({ size = 36 }) {
  return (
    <svg viewBox="0 0 120 120" width={size} height={size} aria-hidden="true" style={{flexShrink:0}}>
      <circle cx="60" cy="60" r="54" fill="none" stroke="var(--ink)" strokeWidth="0.7" strokeDasharray="1 3" opacity="0.55"/>
      <circle cx="60" cy="60" r="28" fill="none" stroke="var(--ink)" strokeWidth="1.6"/>
      <ellipse cx="60" cy="60" rx="28" ry="9" fill="none" stroke="var(--ink)" strokeWidth="0.9"/>
      <ellipse cx="60" cy="60" rx="9"  ry="28" fill="none" stroke="var(--ink)" strokeWidth="0.9"/>
      <ellipse cx="60" cy="60" rx="20" ry="28" fill="none" stroke="var(--ink)" strokeWidth="0.6" opacity="0.5"/>
      <circle cx="60"  cy="6"  r="3.4" fill="var(--ocean)"/>
      <circle cx="114" cy="60" r="2.6" fill="var(--forest)"/>
      <circle cx="60"  cy="114" r="2.1" fill="var(--ochre)"/>
      <circle cx="6"   cy="60" r="2.9" fill="var(--ink)"/>
      <circle cx="98"  cy="22" r="1.9" fill="var(--ink)" opacity="0.5"/>
      <circle cx="22"  cy="98" r="1.9" fill="var(--ink)" opacity="0.5"/>
    </svg>
  );
}

function Masthead() {
  return (
    <header className="masthead">
      <div className="wrap masthead-inner">
        <a href="#" className="wordmark" aria-label="The Small World">
          <OrbitMark size={34}/>
          <span className="wm-text"><b>THE</b> <i>Small</i> <b>WORLD</b></span>
        </a>
        <nav className="meta">
          <a href="#demo">Demo</a>
          <a href="#method">Method</a>
          <a href="#agents">Architecture</a>
          <a href="#theories">Runs</a>
          <a href="#questions">FAQ</a>
          <a href="https://github.com/tusharojha/thesmallworld" target="_blank" rel="noopener" style={{color:"var(--ocean)"}}>GitHub →</a>
        </nav>
      </div>
    </header>
  );
}

function PaperHead() {
  return (
    <div className="paper-head">
      <div className="vol">
        <span><span className="dot"></span>Vol. 1 · Issue 01</span>
        <span>Decision Intelligence</span>
        <span>April 2026</span>
      </div>
      <h1>
        A world simulator for testing real-world theories across thousands of agents.
      </h1>
      <div className="byline">Baselines reconstructed. Leaders grounded. Cascades propagated. Briefs written.</div>
      <div className="affil">The Small World · Open-source, CLI-native</div>

      <div className="abstract">
        <div className="lbl">Abstract</div>
        <div>
          <p>
            <b>The Small World</b> reconstructs a live baseline from source-backed indicators, grounds named leaders
            and institutions against current reality, and propagates a shock through an explicit social graph.
          </p>
          <p>
            Outputs are decision-grade: a current-state reconstruction, a shock-propagation analysis, a system stress
            map, and a decision brief framed for <em>government</em>, <em>central-bank</em>, <em>NGO</em>, or
            <em> enterprise-strategy</em> lenses.
          </p>
          <div className="keywords">
            <b>Keywords</b>decision intelligence · agent-based modeling · shock propagation · grounded leadership · policy simulation
          </div>
        </div>
      </div>
    </div>
  );
}

// ============ TWEAKS ============
function Tweaks({ cfg, setCfg, active, setActive }) {
  useEffect(() => {
    const onMsg = (e) => {
      if (e.data?.type === "__activate_edit_mode") setActive(true);
      if (e.data?.type === "__deactivate_edit_mode") setActive(false);
    };
    window.addEventListener("message", onMsg);
    window.parent.postMessage({ type: "__edit_mode_available" }, "*");
    return () => window.removeEventListener("message", onMsg);
  }, []);

  const update = (k, v) => {
    const next = { ...cfg, [k]: v };
    setCfg(next);
    window.parent.postMessage({ type: "__edit_mode_set_keys", edits: { [k]: v } }, "*");
  };

  const palettes = {
    earth:   { ocean: "#2d5a7c", forest: "#4a7c59", ochre: "#c9a961", crimson: "#8b3a3a" },
    atlas:   { ocean: "#1e40af", forest: "#166534", ochre: "#b45309", crimson: "#991b1b" },
    oxford:  { ocean: "#334155", forest: "#475569", ochre: "#a16207", crimson: "#7f1d1d" },
    archive: { ocean: "#3a6b7c", forest: "#6b8e4e", ochre: "#b85c38", crimson: "#7c2d12" },
  };

  useEffect(() => {
    const p = palettes[cfg.palette] || palettes.earth;
    Object.entries(p).forEach(([k, v]) => document.documentElement.style.setProperty(`--${k}`, v));
    document.documentElement.style.setProperty("--paper", cfg.bg === "cream" ? "#fafaf7" : cfg.bg === "pure" ? "#ffffff" : "#f5f3ee");
  }, [cfg.palette, cfg.bg]);

  if (!active) return null;

  return (
    <div className="tweaks-panel active">
      <h5>Tweaks</h5>
      <div className="sub">Customize the paper</div>

      <div className="grp">
        <div className="lbl">Accent palette</div>
        <div className="opts">
          {["earth","atlas","oxford","archive"].map((p) => (
            <button key={p} className={`opt ${cfg.palette === p ? "active" : ""}`} onClick={() => update("palette", p)}>{p}</button>
          ))}
        </div>
      </div>

      <div className="grp">
        <div className="lbl">Paper</div>
        <div className="opts">
          {["cream","warm","pure"].map((b) => (
            <button key={b} className={`opt ${cfg.bg === b ? "active" : ""}`} onClick={() => update("bg", b)}>{b}</button>
          ))}
        </div>
      </div>

      <div className="grp">
        <div className="lbl">Demo video URL (YouTube)</div>
        <input
          style={{width:"100%", padding:"6px 8px", fontFamily:"var(--mono)", fontSize:"11px", border:"1px solid var(--paper-rule)", background:"var(--paper)", color:"var(--ink)"}}
          value={cfg.videoUrl || ""}
          placeholder="https://youtu.be/xxxxxxxxxxx"
          onChange={(e) => update("videoUrl", e.target.value)}
        />
      </div>

      <div className="grp">
        <div className="lbl">Margin notes</div>
        <div className="opts">
          {["on","off"].map((m) => (
            <button key={m} className={`opt ${cfg.margins === m ? "active" : ""}`} onClick={() => update("margins", m)}>{m}</button>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============ APP ============
function App() {
  const DEFAULTS = /*EDITMODE-BEGIN*/{
    "palette": "earth",
    "bg": "cream",
    "videoUrl": "",
    "margins": "on"
  }/*EDITMODE-END*/;
  const [cfg, setCfg] = useState(DEFAULTS);
  const [tweaksActive, setTweaksActive] = useState(false);

  useEffect(() => {
    if (cfg.margins === "off") {
      document.querySelectorAll(".sec-head .sec-num, .body-col .side, .abstract .lbl").forEach((el) => el.style.display = "none");
      document.querySelectorAll(".sec-head, .body-col, .abstract").forEach((el) => el.style.gridTemplateColumns = "1fr");
    } else {
      document.querySelectorAll(".sec-head .sec-num, .body-col .side, .abstract .lbl").forEach((el) => el.style.display = "");
      document.querySelectorAll(".sec-head, .body-col").forEach((el) => el.style.gridTemplateColumns = "180px 1fr");
      document.querySelectorAll(".abstract").forEach((el) => el.style.gridTemplateColumns = "180px 1fr");
    }
  }, [cfg.margins]);

  return (
    <>
      <Masthead />
      <div className="wrap">
        <PaperHead />
        <CliHero />
        <DemoVideo url={cfg.videoUrl} />
        <LoopDiagram />
        <AgentGraph />
        <Theories />
        <ReportPreview />
        <UseCases />
        <FAQ />
        <CTA />
        <Colophon />
      </div>
      <Tweaks cfg={cfg} setCfg={setCfg} active={tweaksActive} setActive={setTweaksActive} />
    </>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
