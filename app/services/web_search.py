"""
Wrapper di ricerca web per dati di mercato e bandi real-time.
Riuso concettuale di src/tools/search.py da strategic-consulting-crew,
adattato all'architettura BaseAgent/Orchestrator.

IMPORTANTE (coerenza con pii_guard di OrgTransform AI): se in futuro questo
servizio riceve dati sensibili sui soci come parte della query, va sanitizzato
PRIMA di uscire verso l'API esterna — stessa logica del pre-LLM PII guard,
qui applicata al pre-search invece che al pre-prompt.
"""
from __future__ import annotations

import os


class WebSearchService:
    def __init__(self):
        self.serper_api_key = os.getenv("SERPER_API_KEY")

    async def search(self, query: str, max_results: int = 5) -> list[dict]:
        if self.serper_api_key:
            return await self._search_serper(query, max_results)
        try:
            return await self._search_playwright(query, max_results)
        except Exception:
            return await self._search_duckduckgo(query, max_results)

    async def _search_serper(self, query: str, max_results: int) -> list[dict]:
        import httpx
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.serper_api_key},
                json={"q": query, "num": max_results}
            )
            response.raise_for_status()
            data = response.json()
            return [
                {"title": r.get("title"), "snippet": r.get("snippet"), "link": r.get("link")}
                for r in data.get("organic", [])
            ]

    async def _search_playwright(self, query: str, max_results: int) -> list[dict]:
        from playwright.async_api import async_playwright
        import urllib.parse

        encoded_query = urllib.parse.quote_plus(query)
        results = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.goto(
                    f"https://duckduckgo.com/html/?q={encoded_query}",
                    timeout=30000
                )
                elements = await page.query_selector_all(".result")
                for el in elements[:max_results]:
                    title_el = await el.query_selector(".result__title")
                    snippet_el = await el.query_selector(".result__snippet")
                    link_el = await el.query_selector(".result__title a")

                    title = (await title_el.inner_text()).strip() if title_el else ""
                    snippet = (await snippet_el.inner_text()).strip() if snippet_el else ""
                    link = (await link_el.get_attribute("href") or "").strip() if link_el else ""

                    results.append({"title": title, "snippet": snippet, "link": link})
            finally:
                await browser.close()

        return results

    async def _search_duckduckgo(self, query: str, max_results: int) -> list[dict]:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return [
            {"title": r["title"], "snippet": r["body"], "link": r["href"]}
            for r in results
        ]
