import hashlib
import json
import ssl
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path


WORLD_BANK_BASE_URL = "https://api.worldbank.org/v2"
CACHE_DIR = Path(".cache/grounding")
CACHE_TTL_SECONDS = 60 * 60 * 12


COUNTRY_CODES = {
    "Australia": "AU",
    "Brazil": "BR",
    "Canada": "CA",
    "China": "CN",
    "Colombia": "CO",
    "Egypt": "EG",
    "Ethiopia": "ET",
    "France": "FR",
    "Germany": "DE",
    "Ghana": "GH",
    "India": "IN",
    "Indonesia": "ID",
    "Japan": "JP",
    "Mexico": "MX",
    "Nigeria": "NG",
    "Norway": "NO",
    "Poland": "PL",
    "Russia": "RU",
    "Saudi Arabia": "SA",
    "South Korea": "KR",
    "Sweden": "SE",
    "Thailand": "TH",
    "UK": "GB",
    "USA": "US",
}


INDICATORS = {
    "population_total": "SP.POP.TOTL",
    "urban_pct": "SP.URB.TOTL.IN.ZS",
    "age_0_14_pct": "SP.POP.0014.TO.ZS",
    "age_65_plus_pct": "SP.POP.65UP.TO.ZS",
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "inflation": "FP.CPI.TOTL.ZG",
    "unemployment": "SL.UEM.TOTL.ZS",
    "gdp_per_capita_usd": "NY.GDP.PCAP.CD",
}


@dataclass
class CountryStats:
    country: str
    country_code: str
    population_total: float | None = None
    urban_pct: float | None = None
    age_0_14_pct: float | None = None
    age_65_plus_pct: float | None = None
    gdp_growth: float | None = None
    inflation: float | None = None
    unemployment: float | None = None
    gdp_per_capita_usd: float | None = None


def _cache_path(url: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest}.json"


def _fetch_json(url: str) -> object:
    cache_path = _cache_path(url)
    now = time.time()
    if cache_path.exists():
        age = now - cache_path.stat().st_mtime
        if age < CACHE_TTL_SECONDS:
            return json.loads(cache_path.read_text(encoding="utf-8"))

    with urllib.request.urlopen(url, timeout=20, context=_ssl_context()) as response:
        payload = response.read().decode("utf-8")
    cache_path.write_text(payload, encoding="utf-8")
    return json.loads(payload)


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _latest_indicator_value(country_code: str, indicator: str) -> float | None:
    params = urllib.parse.urlencode({
        "format": "json",
        "per_page": 70,
    })
    url = f"{WORLD_BANK_BASE_URL}/country/{country_code}/indicator/{indicator}?{params}"
    payload = _fetch_json(url)
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        return None

    entries = payload[1]
    for entry in entries:
        value = entry.get("value")
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
    return None


def fetch_country_stats(countries: list[str]) -> dict[str, CountryStats]:
    stats: dict[str, CountryStats] = {}
    jobs = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        for country in sorted(set(countries)):
            code = COUNTRY_CODES.get(country)
            if not code:
                continue

            row = CountryStats(country=country, country_code=code)
            stats[country] = row
            for field_name, indicator in INDICATORS.items():
                jobs.append(
                    executor.submit(_latest_indicator_value, code, indicator)
                )
                jobs[-1].country = country  # type: ignore[attr-defined]
                jobs[-1].field_name = field_name  # type: ignore[attr-defined]

        for job in as_completed(jobs):
            country = job.country  # type: ignore[attr-defined]
            field_name = job.field_name  # type: ignore[attr-defined]
            try:
                value = job.result()
            except Exception:
                value = None
            setattr(stats[country], field_name, value)
    return stats


def stats_to_jsonable(stats: dict[str, CountryStats]) -> dict[str, dict]:
    return {country: asdict(row) for country, row in stats.items()}
