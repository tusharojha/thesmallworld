import json
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


class SearchProvider:
    def search(self, query: str, count: int = 5) -> list[SearchResult]:
        raise NotImplementedError


class NullSearchProvider(SearchProvider):
    def search(self, query: str, count: int = 5) -> list[SearchResult]:
        return []


class BraveSearchProvider(SearchProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str, count: int = 5) -> list[SearchResult]:
        params = urllib.parse.urlencode({
            "q": query,
            "count": count,
            "search_lang": "en",
        })
        req = urllib.request.Request(
            f"https://api.search.brave.com/res/v1/web/search?{params}",
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key,
            },
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))

        results: list[SearchResult] = []
        for item in payload.get("web", {}).get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("description", ""),
            ))
        return results


class SearxngSearchProvider(SearchProvider):
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def search(self, query: str, count: int = 5) -> list[SearchResult]:
        params = urllib.parse.urlencode({
            "q": query,
            "format": "json",
        })
        url = f"{self.base_url}/search?{params}"
        with urllib.request.urlopen(url, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))

        results: list[SearchResult] = []
        for item in payload.get("results", [])[:count]:
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", "") or item.get("snippet", ""),
            ))
        return results


def build_search_provider(
    provider_name: str,
    brave_api_key: str | None = None,
    searxng_base_url: str | None = None,
) -> SearchProvider:
    provider_name = (provider_name or "none").lower()
    if provider_name == "brave" and brave_api_key:
        return BraveSearchProvider(brave_api_key)
    if provider_name == "searxng" and searxng_base_url:
        return SearxngSearchProvider(searxng_base_url)
    return NullSearchProvider()
