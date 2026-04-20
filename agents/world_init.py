import networkx as nx
from agents.profile import AgentProfile
from grounding.baseline import CurrentWorldState, calibrate_world_from_current_state


def build_world(current_state: CurrentWorldState | None = None) -> tuple[list[AgentProfile], nx.Graph]:
    agents = _create_archetypes()
    _apply_current_realism_defaults(agents)
    calibrate_world_from_current_state(agents, current_state)
    graph = _build_social_graph(agents)
    return agents, graph


def represented_countries() -> list[str]:
    return sorted({agent.country for agent in _create_archetypes()})


def _create_archetypes() -> list[AgentProfile]:
    raw = [
        # ── UNITED STATES ──────────────────────────────────────────────────────
        dict(id="us_01", name="Marcus", age=52, gender="male", country="USA", city_type="rural",
             income_bracket="lower-middle", education_level="secondary", occupation="factory worker",
             political_ideology=0.7, religious_affiliation="christian", religiosity_level=0.8,
             trust_in_institutions=0.3, openness_to_change=0.2,
             openness=0.3, conscientiousness=0.6, extraversion=0.4, agreeableness=0.5, neuroticism=0.5,
             media_sources=["cable_news_right", "local_radio"], representational_weight=28),

        dict(id="us_02", name="Sofia", age=34, gender="female", country="USA", city_type="urban",
             income_bracket="upper-middle", education_level="postgrad", occupation="software engineer",
             political_ideology=-0.5, religious_affiliation="atheist", religiosity_level=0.1,
             trust_in_institutions=0.55, openness_to_change=0.8,
             openness=0.85, conscientiousness=0.75, extraversion=0.6, agreeableness=0.65, neuroticism=0.3,
             media_sources=["online_liberal_media", "social_media", "podcasts"], representational_weight=22),

        dict(id="us_03", name="Darnell", age=27, gender="male", country="USA", city_type="urban",
             income_bracket="low", education_level="secondary", occupation="gig worker",
             political_ideology=-0.3, religious_affiliation="christian", religiosity_level=0.5,
             trust_in_institutions=0.25, openness_to_change=0.5,
             openness=0.5, conscientiousness=0.4, extraversion=0.65, agreeableness=0.6, neuroticism=0.6,
             media_sources=["social_media", "youtube"], representational_weight=18),

        dict(id="us_04", name="Linda", age=61, gender="female", country="USA", city_type="suburban",
             income_bracket="upper-middle", education_level="tertiary", occupation="nurse",
             political_ideology=0.1, religious_affiliation="christian", religiosity_level=0.6,
             trust_in_institutions=0.6, openness_to_change=0.45,
             openness=0.5, conscientiousness=0.8, extraversion=0.55, agreeableness=0.75, neuroticism=0.35,
             media_sources=["mainstream_tv", "local_news"], representational_weight=25),

        dict(id="us_05", name="Tyler", age=22, gender="male", country="USA", city_type="suburban",
             income_bracket="low", education_level="tertiary", occupation="student",
             political_ideology=-0.6, religious_affiliation="atheist", religiosity_level=0.05,
             trust_in_institutions=0.35, openness_to_change=0.9,
             openness=0.9, conscientiousness=0.45, extraversion=0.7, agreeableness=0.65, neuroticism=0.5,
             media_sources=["social_media", "online_liberal_media", "podcasts"], representational_weight=12),

        # ── EUROPE (UK / Germany / Eastern Europe) ─────────────────────────────
        dict(id="eu_01", name="Ingrid", age=45, gender="female", country="Germany", city_type="urban",
             income_bracket="upper-middle", education_level="postgrad", occupation="teacher",
             political_ideology=-0.2, religious_affiliation="atheist", religiosity_level=0.1,
             trust_in_institutions=0.65, openness_to_change=0.65,
             openness=0.75, conscientiousness=0.8, extraversion=0.5, agreeableness=0.7, neuroticism=0.25,
             media_sources=["public_broadcaster", "online_news"], representational_weight=30),

        dict(id="eu_02", name="Pawel", age=38, gender="male", country="Poland", city_type="rural",
             income_bracket="lower-middle", education_level="secondary", occupation="farmer",
             political_ideology=0.75, religious_affiliation="christian", religiosity_level=0.9,
             trust_in_institutions=0.4, openness_to_change=0.15,
             openness=0.25, conscientiousness=0.65, extraversion=0.4, agreeableness=0.5, neuroticism=0.45,
             media_sources=["local_radio", "cable_news_right"], representational_weight=20),

        dict(id="eu_03", name="Amelia", age=29, gender="female", country="UK", city_type="urban",
             income_bracket="lower-middle", education_level="tertiary", occupation="barista",
             political_ideology=-0.4, religious_affiliation="atheist", religiosity_level=0.05,
             trust_in_institutions=0.3, openness_to_change=0.7,
             openness=0.7, conscientiousness=0.5, extraversion=0.75, agreeableness=0.65, neuroticism=0.55,
             media_sources=["social_media", "online_liberal_media"], representational_weight=18),

        dict(id="eu_04", name="Heinrich", age=67, gender="male", country="Germany", city_type="suburban",
             income_bracket="high", education_level="postgrad", occupation="retired engineer",
             political_ideology=0.3, religious_affiliation="christian", religiosity_level=0.4,
             trust_in_institutions=0.7, openness_to_change=0.35,
             openness=0.55, conscientiousness=0.85, extraversion=0.35, agreeableness=0.6, neuroticism=0.2,
             media_sources=["public_broadcaster", "financial_press"], representational_weight=22),

        dict(id="eu_05", name="Fatima", age=31, gender="female", country="France", city_type="urban",
             income_bracket="lower-middle", education_level="tertiary", occupation="retail worker",
             political_ideology=-0.1, religious_affiliation="muslim", religiosity_level=0.6,
             trust_in_institutions=0.35, openness_to_change=0.5,
             openness=0.55, conscientiousness=0.6, extraversion=0.55, agreeableness=0.65, neuroticism=0.5,
             media_sources=["mainstream_tv", "social_media"], representational_weight=15),

        # ── INDIA ──────────────────────────────────────────────────────────────
        dict(id="in_01", name="Rajesh", age=44, gender="male", country="India", city_type="urban",
             income_bracket="upper-middle", education_level="postgrad", occupation="IT manager",
             political_ideology=0.4, religious_affiliation="hindu", religiosity_level=0.6,
             trust_in_institutions=0.5, openness_to_change=0.55,
             openness=0.65, conscientiousness=0.75, extraversion=0.5, agreeableness=0.6, neuroticism=0.35,
             media_sources=["mainstream_tv", "social_media", "online_news"], representational_weight=40),

        dict(id="in_02", name="Priya", age=26, gender="female", country="India", city_type="urban",
             income_bracket="lower-middle", education_level="tertiary", occupation="call center agent",
             political_ideology=0.0, religious_affiliation="hindu", religiosity_level=0.5,
             trust_in_institutions=0.45, openness_to_change=0.65,
             openness=0.65, conscientiousness=0.65, extraversion=0.6, agreeableness=0.7, neuroticism=0.45,
             media_sources=["social_media", "mainstream_tv"], representational_weight=35),

        dict(id="in_03", name="Suresh", age=55, gender="male", country="India", city_type="rural",
             income_bracket="low", education_level="primary", occupation="subsistence farmer",
             political_ideology=0.5, religious_affiliation="hindu", religiosity_level=0.85,
             trust_in_institutions=0.55, openness_to_change=0.2,
             openness=0.2, conscientiousness=0.6, extraversion=0.35, agreeableness=0.65, neuroticism=0.4,
             media_sources=["local_radio", "word_of_mouth"], representational_weight=80),

        dict(id="in_04", name="Aisha", age=33, gender="female", country="India", city_type="urban",
             income_bracket="lower-middle", education_level="secondary", occupation="domestic worker",
             political_ideology=-0.1, religious_affiliation="muslim", religiosity_level=0.7,
             trust_in_institutions=0.3, openness_to_change=0.4,
             openness=0.4, conscientiousness=0.55, extraversion=0.45, agreeableness=0.7, neuroticism=0.55,
             media_sources=["social_media", "word_of_mouth"], representational_weight=25),

        dict(id="in_05", name="Arjun", age=21, gender="male", country="India", city_type="urban",
             income_bracket="lower-middle", education_level="tertiary", occupation="student",
             political_ideology=-0.2, religious_affiliation="atheist", religiosity_level=0.1,
             trust_in_institutions=0.35, openness_to_change=0.85,
             openness=0.85, conscientiousness=0.55, extraversion=0.75, agreeableness=0.6, neuroticism=0.5,
             media_sources=["social_media", "youtube", "online_news"], representational_weight=30),

        # ── BRAZIL ─────────────────────────────────────────────────────────────
        dict(id="br_01", name="Ana", age=39, gender="female", country="Brazil", city_type="urban",
             income_bracket="lower-middle", education_level="tertiary", occupation="teacher",
             political_ideology=-0.4, religious_affiliation="christian", religiosity_level=0.7,
             trust_in_institutions=0.3, openness_to_change=0.6,
             openness=0.6, conscientiousness=0.7, extraversion=0.65, agreeableness=0.75, neuroticism=0.5,
             media_sources=["mainstream_tv", "social_media"], representational_weight=35),

        dict(id="br_02", name="Carlos", age=48, gender="male", country="Brazil", city_type="urban",
             income_bracket="high", education_level="postgrad", occupation="business owner",
             political_ideology=0.65, religious_affiliation="christian", religiosity_level=0.5,
             trust_in_institutions=0.45, openness_to_change=0.35,
             openness=0.45, conscientiousness=0.75, extraversion=0.65, agreeableness=0.45, neuroticism=0.35,
             media_sources=["financial_press", "mainstream_tv", "online_news"], representational_weight=15),

        dict(id="br_03", name="Maria", age=62, gender="female", country="Brazil", city_type="rural",
             income_bracket="low", education_level="primary", occupation="subsistence farmer",
             political_ideology=0.3, religious_affiliation="christian", religiosity_level=0.9,
             trust_in_institutions=0.5, openness_to_change=0.2,
             openness=0.2, conscientiousness=0.65, extraversion=0.5, agreeableness=0.8, neuroticism=0.4,
             media_sources=["local_radio", "word_of_mouth"], representational_weight=28),

        dict(id="br_04", name="Gabriel", age=24, gender="male", country="Brazil", city_type="urban",
             income_bracket="low", education_level="secondary", occupation="delivery driver",
             political_ideology=0.0, religious_affiliation="christian", religiosity_level=0.4,
             trust_in_institutions=0.2, openness_to_change=0.55,
             openness=0.5, conscientiousness=0.45, extraversion=0.7, agreeableness=0.6, neuroticism=0.6,
             media_sources=["social_media", "youtube"], representational_weight=22),

        dict(id="br_05", name="Lucia", age=35, gender="female", country="Brazil", city_type="suburban",
             income_bracket="upper-middle", education_level="postgrad", occupation="doctor",
             political_ideology=-0.3, religious_affiliation="atheist", religiosity_level=0.1,
             trust_in_institutions=0.55, openness_to_change=0.7,
             openness=0.75, conscientiousness=0.85, extraversion=0.5, agreeableness=0.65, neuroticism=0.3,
             media_sources=["online_news", "public_broadcaster", "podcasts"], representational_weight=18),

        # ── NIGERIA ────────────────────────────────────────────────────────────
        dict(id="ng_01", name="Emeka", age=30, gender="male", country="Nigeria", city_type="urban",
             income_bracket="lower-middle", education_level="tertiary", occupation="street trader",
             political_ideology=0.2, religious_affiliation="christian", religiosity_level=0.85,
             trust_in_institutions=0.2, openness_to_change=0.6,
             openness=0.55, conscientiousness=0.6, extraversion=0.8, agreeableness=0.65, neuroticism=0.55,
             media_sources=["social_media", "local_radio"], representational_weight=45),

        dict(id="ng_02", name="Halima", age=28, gender="female", country="Nigeria", city_type="rural",
             income_bracket="low", education_level="primary", occupation="subsistence farmer",
             political_ideology=0.1, religious_affiliation="muslim", religiosity_level=0.9,
             trust_in_institutions=0.4, openness_to_change=0.25,
             openness=0.25, conscientiousness=0.6, extraversion=0.45, agreeableness=0.75, neuroticism=0.4,
             media_sources=["local_radio", "word_of_mouth"], representational_weight=55),

        dict(id="ng_03", name="Chidi", age=42, gender="male", country="Nigeria", city_type="urban",
             income_bracket="upper-middle", education_level="postgrad", occupation="lawyer",
             political_ideology=-0.1, religious_affiliation="christian", religiosity_level=0.6,
             trust_in_institutions=0.35, openness_to_change=0.55,
             openness=0.65, conscientiousness=0.8, extraversion=0.6, agreeableness=0.55, neuroticism=0.3,
             media_sources=["online_news", "mainstream_tv", "social_media"], representational_weight=12),

        dict(id="ng_04", name="Amina", age=19, gender="female", country="Nigeria", city_type="urban",
             income_bracket="low", education_level="secondary", occupation="student",
             political_ideology=-0.2, religious_affiliation="muslim", religiosity_level=0.7,
             trust_in_institutions=0.25, openness_to_change=0.75,
             openness=0.7, conscientiousness=0.55, extraversion=0.7, agreeableness=0.7, neuroticism=0.5,
             media_sources=["social_media", "youtube"], representational_weight=30),

        dict(id="ng_05", name="Babatunde", age=55, gender="male", country="Nigeria", city_type="rural",
             income_bracket="lower-middle", education_level="secondary", occupation="trader",
             political_ideology=0.4, religious_affiliation="christian", religiosity_level=0.8,
             trust_in_institutions=0.35, openness_to_change=0.3,
             openness=0.3, conscientiousness=0.65, extraversion=0.55, agreeableness=0.6, neuroticism=0.4,
             media_sources=["local_radio", "word_of_mouth", "mainstream_tv"], representational_weight=38),

        # ── CHINA ──────────────────────────────────────────────────────────────
        dict(id="cn_01", name="Wei", age=35, gender="male", country="China", city_type="urban",
             income_bracket="upper-middle", education_level="postgrad", occupation="engineer",
             political_ideology=0.3, religious_affiliation="atheist", religiosity_level=0.05,
             trust_in_institutions=0.65, openness_to_change=0.5,
             openness=0.6, conscientiousness=0.85, extraversion=0.45, agreeableness=0.55, neuroticism=0.3,
             media_sources=["state_media", "social_media_domestic"], representational_weight=60),

        dict(id="cn_02", name="Mei", age=24, gender="female", country="China", city_type="urban",
             income_bracket="lower-middle", education_level="tertiary", occupation="factory worker",
             political_ideology=0.2, religious_affiliation="atheist", religiosity_level=0.05,
             trust_in_institutions=0.6, openness_to_change=0.45,
             openness=0.5, conscientiousness=0.7, extraversion=0.5, agreeableness=0.65, neuroticism=0.45,
             media_sources=["state_media", "social_media_domestic"], representational_weight=80),

        dict(id="cn_03", name="Liang", age=58, gender="male", country="China", city_type="rural",
             income_bracket="low", education_level="primary", occupation="subsistence farmer",
             political_ideology=0.3, religious_affiliation="atheist", religiosity_level=0.1,
             trust_in_institutions=0.7, openness_to_change=0.2,
             openness=0.2, conscientiousness=0.65, extraversion=0.35, agreeableness=0.6, neuroticism=0.35,
             media_sources=["state_media", "word_of_mouth"], representational_weight=120),

        # ── MIDDLE EAST ────────────────────────────────────────────────────────
        dict(id="me_01", name="Omar", age=32, gender="male", country="Egypt", city_type="urban",
             income_bracket="lower-middle", education_level="tertiary", occupation="teacher",
             political_ideology=0.1, religious_affiliation="muslim", religiosity_level=0.85,
             trust_in_institutions=0.35, openness_to_change=0.4,
             openness=0.45, conscientiousness=0.65, extraversion=0.55, agreeableness=0.65, neuroticism=0.45,
             media_sources=["mainstream_tv", "social_media"], representational_weight=35),

        dict(id="me_02", name="Layla", age=27, gender="female", country="Saudi Arabia", city_type="urban",
             income_bracket="high", education_level="postgrad", occupation="consultant",
             political_ideology=0.2, religious_affiliation="muslim", religiosity_level=0.6,
             trust_in_institutions=0.55, openness_to_change=0.65,
             openness=0.65, conscientiousness=0.75, extraversion=0.6, agreeableness=0.6, neuroticism=0.35,
             media_sources=["online_news", "social_media", "podcasts"], representational_weight=10),

        # ── SOUTHEAST ASIA ─────────────────────────────────────────────────────
        dict(id="sea_01", name="Nong", age=41, gender="female", country="Thailand", city_type="rural",
             income_bracket="low", education_level="secondary", occupation="rice farmer",
             political_ideology=0.15, religious_affiliation="buddhist", religiosity_level=0.8,
             trust_in_institutions=0.5, openness_to_change=0.3,
             openness=0.3, conscientiousness=0.6, extraversion=0.45, agreeableness=0.75, neuroticism=0.35,
             media_sources=["mainstream_tv", "word_of_mouth"], representational_weight=25),

        dict(id="sea_02", name="Budi", age=29, gender="male", country="Indonesia", city_type="urban",
             income_bracket="lower-middle", education_level="tertiary", occupation="driver",
             political_ideology=0.1, religious_affiliation="muslim", religiosity_level=0.75,
             trust_in_institutions=0.4, openness_to_change=0.5,
             openness=0.5, conscientiousness=0.55, extraversion=0.65, agreeableness=0.65, neuroticism=0.5,
             media_sources=["social_media", "mainstream_tv"], representational_weight=40),

        # ── LATIN AMERICA (ex Brazil) ──────────────────────────────────────────
        dict(id="la_01", name="Diego", age=36, gender="male", country="Mexico", city_type="urban",
             income_bracket="lower-middle", education_level="secondary", occupation="construction worker",
             political_ideology=0.0, religious_affiliation="christian", religiosity_level=0.65,
             trust_in_institutions=0.2, openness_to_change=0.5,
             openness=0.45, conscientiousness=0.55, extraversion=0.6, agreeableness=0.65, neuroticism=0.55,
             media_sources=["mainstream_tv", "social_media"], representational_weight=30),

        dict(id="la_02", name="Valentina", age=23, gender="female", country="Colombia", city_type="urban",
             income_bracket="lower-middle", education_level="tertiary", occupation="student",
             political_ideology=-0.35, religious_affiliation="christian", religiosity_level=0.4,
             trust_in_institutions=0.25, openness_to_change=0.8,
             openness=0.8, conscientiousness=0.6, extraversion=0.75, agreeableness=0.7, neuroticism=0.5,
             media_sources=["social_media", "online_news", "podcasts"], representational_weight=15),

        # ── SUB-SAHARAN AFRICA (ex Nigeria) ────────────────────────────────────
        dict(id="ssa_01", name="Amara", age=25, gender="female", country="Ethiopia", city_type="rural",
             income_bracket="low", education_level="none", occupation="subsistence farmer",
             political_ideology=0.0, religious_affiliation="christian", religiosity_level=0.9,
             trust_in_institutions=0.5, openness_to_change=0.3,
             openness=0.25, conscientiousness=0.6, extraversion=0.4, agreeableness=0.75, neuroticism=0.4,
             media_sources=["local_radio", "word_of_mouth"], representational_weight=60),

        dict(id="ssa_02", name="Kwame", age=34, gender="male", country="Ghana", city_type="urban",
             income_bracket="lower-middle", education_level="tertiary", occupation="journalist",
             political_ideology=-0.2, religious_affiliation="christian", religiosity_level=0.6,
             trust_in_institutions=0.4, openness_to_change=0.7,
             openness=0.75, conscientiousness=0.7, extraversion=0.7, agreeableness=0.6, neuroticism=0.4,
             media_sources=["online_news", "social_media", "mainstream_tv"], representational_weight=8),

        # ── RUSSIA / EASTERN EUROPE ────────────────────────────────────────────
        dict(id="ru_01", name="Dmitri", age=47, gender="male", country="Russia", city_type="urban",
             income_bracket="lower-middle", education_level="secondary", occupation="factory worker",
             political_ideology=0.6, religious_affiliation="christian", religiosity_level=0.5,
             trust_in_institutions=0.55, openness_to_change=0.2,
             openness=0.25, conscientiousness=0.6, extraversion=0.4, agreeableness=0.45, neuroticism=0.45,
             media_sources=["state_media", "mainstream_tv"], representational_weight=35),

        dict(id="ru_02", name="Katya", age=29, gender="female", country="Russia", city_type="urban",
             income_bracket="upper-middle", education_level="postgrad", occupation="programmer",
             political_ideology=-0.3, religious_affiliation="atheist", religiosity_level=0.05,
             trust_in_institutions=0.2, openness_to_change=0.75,
             openness=0.8, conscientiousness=0.7, extraversion=0.55, agreeableness=0.6, neuroticism=0.45,
             media_sources=["vpn_foreign_media", "social_media", "podcasts"], representational_weight=15),

        # ── JAPAN / SOUTH KOREA ────────────────────────────────────────────────
        dict(id="jp_01", name="Hiroshi", age=53, gender="male", country="Japan", city_type="urban",
             income_bracket="upper-middle", education_level="postgrad", occupation="corporate manager",
             political_ideology=0.25, religious_affiliation="buddhist", religiosity_level=0.3,
             trust_in_institutions=0.6, openness_to_change=0.3,
             openness=0.4, conscientiousness=0.9, extraversion=0.35, agreeableness=0.65, neuroticism=0.35,
             media_sources=["mainstream_tv", "financial_press"], representational_weight=20),

        dict(id="kr_01", name="Jisoo", age=26, gender="female", country="South Korea", city_type="urban",
             income_bracket="lower-middle", education_level="tertiary", occupation="office worker",
             political_ideology=-0.1, religious_affiliation="christian", religiosity_level=0.4,
             trust_in_institutions=0.4, openness_to_change=0.6,
             openness=0.65, conscientiousness=0.75, extraversion=0.6, agreeableness=0.65, neuroticism=0.5,
             media_sources=["social_media", "online_news", "mainstream_tv"], representational_weight=18),

        # ── SCANDINAVIA / WESTERN EUROPE ───────────────────────────────────────
        dict(id="sc_01", name="Erik", age=40, gender="male", country="Sweden", city_type="urban",
             income_bracket="upper-middle", education_level="postgrad", occupation="researcher",
             political_ideology=-0.4, religious_affiliation="atheist", religiosity_level=0.05,
             trust_in_institutions=0.8, openness_to_change=0.75,
             openness=0.85, conscientiousness=0.75, extraversion=0.5, agreeableness=0.7, neuroticism=0.2,
             media_sources=["public_broadcaster", "online_news", "podcasts"], representational_weight=12),

        dict(id="sc_02", name="Astrid", age=33, gender="female", country="Norway", city_type="urban",
             income_bracket="high", education_level="postgrad", occupation="policy analyst",
             political_ideology=-0.45, religious_affiliation="atheist", religiosity_level=0.05,
             trust_in_institutions=0.8, openness_to_change=0.8,
             openness=0.85, conscientiousness=0.8, extraversion=0.55, agreeableness=0.75, neuroticism=0.2,
             media_sources=["public_broadcaster", "online_news"], representational_weight=10),

        # ── CANADA / AUSTRALIA ────────────────────────────────────────────────
        dict(id="ca_01", name="Liam", age=31, gender="male", country="Canada", city_type="suburban",
             income_bracket="upper-middle", education_level="tertiary", occupation="accountant",
             political_ideology=0.1, religious_affiliation="atheist", religiosity_level=0.1,
             trust_in_institutions=0.55, openness_to_change=0.6,
             openness=0.6, conscientiousness=0.75, extraversion=0.55, agreeableness=0.65, neuroticism=0.35,
             media_sources=["public_broadcaster", "online_news", "social_media"], representational_weight=15),

        dict(id="au_01", name="Sarah", age=44, gender="female", country="Australia", city_type="suburban",
             income_bracket="upper-middle", education_level="tertiary", occupation="small business owner",
             political_ideology=0.2, religious_affiliation="christian", religiosity_level=0.35,
             trust_in_institutions=0.5, openness_to_change=0.5,
             openness=0.55, conscientiousness=0.7, extraversion=0.65, agreeableness=0.65, neuroticism=0.35,
             media_sources=["mainstream_tv", "online_news", "social_media"], representational_weight=12),

        # ── WEALTHY ELITE (global) ─────────────────────────────────────────────
        dict(id="el_01", name="Alexander", age=50, gender="male", country="USA", city_type="urban",
             income_bracket="high", education_level="postgrad", occupation="hedge fund manager",
             political_ideology=0.5, religious_affiliation="atheist", religiosity_level=0.05,
             trust_in_institutions=0.7, openness_to_change=0.4,
             openness=0.55, conscientiousness=0.85, extraversion=0.6, agreeableness=0.35, neuroticism=0.2,
             media_sources=["financial_press", "podcasts", "online_news"], representational_weight=2),

        dict(id="el_02", name="Nadia", age=38, gender="female", country="UK", city_type="urban",
             income_bracket="high", education_level="postgrad", occupation="CEO",
             political_ideology=-0.1, religious_affiliation="atheist", religiosity_level=0.05,
             trust_in_institutions=0.6, openness_to_change=0.65,
             openness=0.7, conscientiousness=0.9, extraversion=0.7, agreeableness=0.5, neuroticism=0.2,
             media_sources=["financial_press", "online_news", "podcasts"], representational_weight=1),

        # ── JOURNALIST / INFLUENCER TIER ──────────────────────────────────────
        dict(id="inf_01", name="Tariq", age=36, gender="male", country="USA", city_type="urban",
             income_bracket="upper-middle", education_level="postgrad", occupation="journalist",
             political_ideology=-0.3, religious_affiliation="atheist", religiosity_level=0.05,
             trust_in_institutions=0.35, openness_to_change=0.75,
             openness=0.8, conscientiousness=0.7, extraversion=0.8, agreeableness=0.5, neuroticism=0.4,
             media_sources=["online_liberal_media", "social_media", "podcasts"], representational_weight=3),

        dict(id="inf_02", name="Tucker_analog", age=48, gender="male", country="USA", city_type="suburban",
             income_bracket="high", education_level="tertiary", occupation="right-wing media host",
             political_ideology=0.85, religious_affiliation="christian", religiosity_level=0.5,
             trust_in_institutions=0.25, openness_to_change=0.15,
             openness=0.3, conscientiousness=0.6, extraversion=0.9, agreeableness=0.3, neuroticism=0.35,
             media_sources=["cable_news_right", "online_news"], representational_weight=2),

        dict(id="inf_03", name="Anika", age=30, gender="female", country="India", city_type="urban",
             income_bracket="upper-middle", education_level="postgrad", occupation="social media influencer",
             political_ideology=-0.15, religious_affiliation="hindu", religiosity_level=0.3,
             trust_in_institutions=0.4, openness_to_change=0.8,
             openness=0.85, conscientiousness=0.6, extraversion=0.9, agreeableness=0.65, neuroticism=0.4,
             media_sources=["social_media", "online_news", "podcasts"], representational_weight=2),

        # ── POLITICIAN TIER ────────────────────────────────────────────────────
        dict(id="pol_01", name="Senator_Morrison", age=56, gender="male", country="USA", city_type="suburban",
             income_bracket="high", education_level="postgrad", occupation="senator (right)",
             political_ideology=0.75, religious_affiliation="christian", religiosity_level=0.65,
             trust_in_institutions=0.5, openness_to_change=0.2,
             openness=0.35, conscientiousness=0.75, extraversion=0.75, agreeableness=0.4, neuroticism=0.25,
             media_sources=["cable_news_right", "financial_press", "online_news"], representational_weight=1),

        dict(id="pol_02", name="Representative_Chen", age=44, gender="female", country="USA", city_type="urban",
             income_bracket="upper-middle", education_level="postgrad", occupation="congressperson (left)",
             political_ideology=-0.65, religious_affiliation="atheist", religiosity_level=0.05,
             trust_in_institutions=0.5, openness_to_change=0.8,
             openness=0.8, conscientiousness=0.8, extraversion=0.75, agreeableness=0.6, neuroticism=0.3,
             media_sources=["online_liberal_media", "social_media", "public_broadcaster"], representational_weight=1),
    ]

    agents = [AgentProfile(**d) for d in raw]
    return agents


def _build_social_graph(agents: list[AgentProfile]) -> nx.Graph:
    g = nx.Graph()
    for a in agents:
        g.add_node(a.id)

    id_map = {a.id: a for a in agents}

    # Connect agents with similar country + city_type (local community ties)
    for i, a in enumerate(agents):
        for b in agents[i + 1:]:
            weight = 0.0
            # Same country → stronger tie
            if a.country == b.country:
                weight += 0.4
            # Same city type → moderate tie
            if a.city_type == b.city_type:
                weight += 0.1
            # Similar ideology (within 0.3) → echo chamber tie
            if abs(a.political_ideology - b.political_ideology) < 0.3:
                weight += 0.2
            # Shared distrust and grievance can also create tight ties
            if abs(a.trust_in_institutions - b.trust_in_institutions) < 0.2:
                weight += 0.1
            if abs(a.change_fatigue - b.change_fatigue) < 0.2:
                weight += 0.05
            # Shared media sources → information tie
            shared_media = set(a.media_sources) & set(b.media_sources)
            weight += len(shared_media) * 0.1
            # Influencers and journalists connect broadly
            if a.occupation in ("journalist", "right-wing media host", "social media influencer",
                                 "senator (right)", "congressperson (left)") or \
               b.occupation in ("journalist", "right-wing media host", "social media influencer",
                                 "senator (right)", "congressperson (left)"):
                weight += 0.3

            if weight >= 0.5:
                g.add_edge(a.id, b.id, weight=weight)

    # Assign connections back to profiles
    for a in agents:
        a.social_connections = list(g.neighbors(a.id))

    return g


def _apply_current_realism_defaults(agents: list[AgentProfile]) -> None:
    for agent in agents:
        income_stress = {
            "low": 0.85,
            "lower-middle": 0.65,
            "upper-middle": 0.35,
            "high": 0.15,
        }.get(agent.income_bracket, 0.5)
        education_buffer = {
            "none": -0.08,
            "primary": -0.06,
            "secondary": -0.03,
            "tertiary": 0.02,
            "postgrad": 0.05,
        }.get(agent.education_level, 0.0)

        distrust_delta = 0.12 if income_stress >= 0.65 else 0.0
        if agent.media_sources and any(src in agent.media_sources for src in ("social_media", "youtube", "word_of_mouth")):
            distrust_delta += 0.05
        if agent.media_sources and any(src in agent.media_sources for src in ("cable_news_right", "vpn_foreign_media")):
            distrust_delta += 0.07

        agent.trust_in_institutions = _clamp(agent.trust_in_institutions - distrust_delta + education_buffer, 0.05, 0.85)
        agent.media_trust = _clamp(
            0.52
            - distrust_delta
            + (0.08 if "public_broadcaster" in agent.media_sources else 0.0)
            - (0.12 if any(src in agent.media_sources for src in ("youtube", "word_of_mouth")) else 0.0)
            - (0.08 if "social_media" in agent.media_sources else 0.0)
            + (0.05 if "state_media" in agent.media_sources else 0.0),
            0.05,
            0.85,
        )
        agent.political_efficacy = _clamp(
            0.48
            + (0.16 if agent.occupation in ("senator (right)", "congressperson (left)", "CEO", "journalist") else 0.0)
            + education_buffer
            - (0.12 if income_stress >= 0.65 else 0.0),
            0.05,
            0.9,
        )
        agent.change_fatigue = _clamp(
            0.35
            + income_stress * 0.45
            + agent.neuroticism * 0.15
            - agent.openness_to_change * 0.2,
            0.05,
            0.95,
        )
        agent.status_quo_bias = _clamp(
            0.38
            + (0.18 if abs(agent.political_ideology) >= 0.45 else 0.0)
            + (0.18 if agent.age >= 50 else 0.0)
            + agent.change_fatigue * 0.2
            - agent.openness_to_change * 0.25,
            0.05,
            0.95,
        )
        agent.social_trust = _clamp(
            0.48 + (agent.agreeableness - 0.5) * 0.4 - distrust_delta * 0.5,
            0.05,
            0.9,
        )
        agent.conflict_orientation = _clamp(
            0.24
            + abs(agent.political_ideology) * 0.35
            + (0.18 if agent.media_trust <= 0.25 else 0.0)
            + (0.12 if agent.trust_in_institutions <= 0.25 else 0.0)
            + (0.08 if agent.occupation in ("right-wing media host", "journalist", "senator (right)", "congressperson (left)") else 0.0)
            - agent.agreeableness * 0.15,
            0.05,
            0.95,
        )
        agent.openness_to_change = _clamp(
            agent.openness_to_change
            - agent.change_fatigue * 0.18
            - agent.status_quo_bias * 0.1
            + education_buffer * 0.5,
            0.05,
            0.95,
        )
        agent.agreeableness = _clamp(
            agent.agreeableness - agent.conflict_orientation * 0.12,
            0.15,
            0.9,
        )
        agent.neuroticism = _clamp(
            agent.neuroticism + income_stress * 0.08 + (0.08 if agent.media_trust <= 0.2 else 0.0),
            0.05,
            0.95,
        )

        if agent.trust_in_institutions <= 0.2 and agent.media_trust <= 0.2:
            agent.emotional_state = "resigned"
        elif agent.change_fatigue >= 0.72 and agent.conflict_orientation >= 0.55:
            agent.emotional_state = "angry"


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
