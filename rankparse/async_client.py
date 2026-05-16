import httpx
from ._client import BaseClient, DEFAULT_BASE_URL
from typing import Any, Optional


class AsyncRankParseClient(BaseClient):
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0) -> None:
        super().__init__(api_key, base_url, timeout)
        self._http = httpx.AsyncClient(base_url=self._base_url, headers=self._headers, timeout=self._timeout)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()

    async def _get(self, path: str, **params) -> Any:
        p = self._build_params(**params)
        r = await self._http.get(path, params=p)
        self._raise_for_status(r)
        return r.json()

    async def _post(self, path: str, body: Any = None) -> Any:
        r = await self._http.post(path, json=body)
        self._raise_for_status(r)
        return r.json()

    async def _delete(self, path: str) -> None:
        r = await self._http.delete(path)
        self._raise_for_status(r)

    # -- Link graph --------------------------------------------------------------

    async def backlinks(self, domain: str, *, limit: int = 100, offset: int = 0,
                        sort: str = "importance", from_domain: Optional[str] = None,
                        link_type: Optional[str] = None) -> dict:
        return await self._get("/backlinks", domain=domain, limit=limit, offset=offset,
                               sort=sort, from_domain=from_domain, link_type=link_type)

    async def referring_domains(self, domain: str, *, limit: int = 100, offset: int = 0) -> dict:
        return await self._get("/referring-domains", domain=domain, limit=limit, offset=offset)

    async def outbound_links(self, domain: str, *, limit: int = 100) -> dict:
        return await self._get("/outbound-links", domain=domain, limit=limit)

    async def anchor_text(self, domain: str, *, limit: int = 100) -> dict:
        return await self._get("/anchor-text", domain=domain, limit=limit)

    async def link_velocity(self, domain: str) -> dict:
        return await self._get("/link-velocity", domain=domain)

    async def new_links(self, domain: str) -> dict:
        return await self._get("/new-links", domain=domain)

    async def lost_links(self, domain: str) -> dict:
        return await self._get("/lost-links", domain=domain)

    async def link_intersect(self, domain_a: str, domain_b: str, *, limit: int = 100) -> dict:
        return await self._get("/link-intersect", domain_a=domain_a, domain_b=domain_b, limit=limit)

    # -- Domain intelligence ----------------------------------------------------

    async def domain_authority(self, domain: str) -> dict:
        return await self._get("/domain-authority", domain=domain)

    async def domain_rank(self, domain: str) -> dict:
        return await self._get("/domain-rank", domain=domain)

    async def domain_overlap(self, domains: list, *, limit: int = 100) -> dict:
        return await self._get("/domain-overlap", domains=domains, limit=limit)

    async def similar_domains(self, domain: str, *, limit: int = 100) -> dict:
        return await self._get("/similar-domains", domain=domain, limit=limit)

    async def competitor_gap(self, domain: str, vs: str, *, limit: int = 50) -> dict:
        return await self._get("/competitor-gap", domain=domain, vs=vs, limit=limit)

    async def link_audit(self, domain: str) -> dict:
        return await self._get("/link-audit", domain=domain)

    async def site_explorer(self, domain: str, *, limit: int = 100) -> dict:
        return await self._get("/site-explorer", domain=domain, limit=limit)

    # -- Page / site ------------------------------------------------------------

    async def page_seo(self, url: str) -> dict:
        return await self._get("/page-seo", url=url)

    async def page_performance(self, url: str, *, strategy: str = "mobile") -> dict:
        return await self._get("/page-performance", url=url, strategy=strategy)

    async def tech_stack(self, url: str) -> dict:
        return await self._get("/tech-stack", url=url)

    async def site_health(self, domain: str) -> dict:
        return await self._get("/site-health", domain=domain)

    async def sitemap(self, domain: str) -> dict:
        return await self._get("/sitemap", domain=domain)

    async def crawl_history(self, domain: str, *, limit: int = 100, offset: int = 0) -> dict:
        return await self._get("/crawl-history", domain=domain, limit=limit, offset=offset)

    async def schema_markup(self, url: str) -> dict:
        return await self._get("/schema-markup", url=url)

    async def internal_links(self, url: str, *, limit: int = 100, offset: int = 0) -> dict:
        return await self._get("/internal-links", url=url, limit=limit, offset=offset)

    async def top_pages(self, domain: str, *, limit: int = 100) -> dict:
        return await self._get("/top-pages", domain=domain, limit=limit)

    # -- Batch ------------------------------------------------------------------

    async def batch(self, requests: list) -> dict:
        return await self._post("/batch", {"requests": requests})

    # -- Dashboard --------------------------------------------------------------

    async def me(self) -> dict:
        return await self._get("/me")

    async def credits(self) -> dict:
        return await self._get("/credits")

    async def keys(self) -> list:
        res = await self._get("/keys")
        return res.get("keys", [])

    async def create_key(self, name: str = "Default") -> dict:
        return await self._post("/keys", {"name": name})

    async def revoke_key(self, key_id: str) -> None:
        await self._delete(f"/keys/{key_id}")

    async def usage(self, *, limit: int = 50, offset: int = 0) -> dict:
        return await self._get("/usage", limit=limit, offset=offset)

    async def checkout(self, pack_id: str) -> dict:
        return await self._post("/checkout", {"pack_id": pack_id})
