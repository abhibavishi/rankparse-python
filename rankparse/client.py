import httpx
from ._client import BaseClient, DEFAULT_BASE_URL
from typing import Any, Optional


class RankParseClient(BaseClient):
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0) -> None:
        super().__init__(api_key, base_url, timeout)
        self._http = httpx.Client(base_url=self._base_url, headers=self._headers, timeout=self._timeout)

    def close(self) -> None:
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _get(self, path: str, **params) -> Any:
        p = self._build_params(**params)
        r = self._http.get(path, params=p)
        self._raise_for_status(r)
        return r.json()

    def _post(self, path: str, body: Any = None) -> Any:
        r = self._http.post(path, json=body)
        self._raise_for_status(r)
        return r.json()

    def _delete(self, path: str) -> None:
        r = self._http.delete(path)
        self._raise_for_status(r)

    # -- Link graph --------------------------------------------------------------

    def backlinks(self, domain: str, *, limit: int = 100, offset: int = 0,
                  sort: str = "importance", from_domain: Optional[str] = None,
                  link_type: Optional[str] = None) -> dict:
        return self._get("/backlinks", domain=domain, limit=limit, offset=offset,
                         sort=sort, from_domain=from_domain, link_type=link_type)

    def referring_domains(self, domain: str, *, limit: int = 100, offset: int = 0) -> dict:
        return self._get("/referring-domains", domain=domain, limit=limit, offset=offset)

    def outbound_links(self, domain: str, *, limit: int = 100) -> dict:
        return self._get("/outbound-links", domain=domain, limit=limit)

    def anchor_text(self, domain: str, *, limit: int = 100) -> dict:
        return self._get("/anchor-text", domain=domain, limit=limit)

    def link_velocity(self, domain: str) -> dict:
        return self._get("/link-velocity", domain=domain)

    def new_links(self, domain: str) -> dict:
        return self._get("/new-links", domain=domain)

    def lost_links(self, domain: str) -> dict:
        return self._get("/lost-links", domain=domain)

    def link_intersect(self, domain_a: str, domain_b: str, *, limit: int = 100) -> dict:
        return self._get("/link-intersect", domain_a=domain_a, domain_b=domain_b, limit=limit)

    # -- Domain intelligence ----------------------------------------------------

    def domain_authority(self, domain: str) -> dict:
        return self._get("/domain-authority", domain=domain)

    def domain_rank(self, domain: str) -> dict:
        return self._get("/domain-rank", domain=domain)

    def domain_overlap(self, domains: list, *, limit: int = 100) -> dict:
        return self._get("/domain-overlap", domains=domains, limit=limit)

    def similar_domains(self, domain: str, *, limit: int = 100) -> dict:
        return self._get("/similar-domains", domain=domain, limit=limit)

    def competitor_gap(self, domain: str, vs: str, *, limit: int = 50) -> dict:
        return self._get("/competitor-gap", domain=domain, vs=vs, limit=limit)

    def link_audit(self, domain: str) -> dict:
        return self._get("/link-audit", domain=domain)

    def site_explorer(self, domain: str, *, limit: int = 100) -> dict:
        return self._get("/site-explorer", domain=domain, limit=limit)

    # -- Page / site ------------------------------------------------------------

    def page_seo(self, url: str) -> dict:
        return self._get("/page-seo", url=url)

    def page_performance(self, url: str, *, strategy: str = "mobile") -> dict:
        return self._get("/page-performance", url=url, strategy=strategy)

    def tech_stack(self, url: str) -> dict:
        return self._get("/tech-stack", url=url)

    def site_health(self, domain: str) -> dict:
        return self._get("/site-health", domain=domain)

    def sitemap(self, domain: str) -> dict:
        return self._get("/sitemap", domain=domain)

    def crawl_history(self, domain: str, *, limit: int = 100, offset: int = 0) -> dict:
        return self._get("/crawl-history", domain=domain, limit=limit, offset=offset)

    def schema_markup(self, url: str) -> dict:
        return self._get("/schema-markup", url=url)

    def internal_links(self, url: str, *, limit: int = 100, offset: int = 0) -> dict:
        return self._get("/internal-links", url=url, limit=limit, offset=offset)

    def top_pages(self, domain: str, *, limit: int = 100) -> dict:
        return self._get("/top-pages", domain=domain, limit=limit)

    # -- Batch ------------------------------------------------------------------

    def batch(self, requests: list) -> dict:
        return self._post("/batch", {"requests": requests})

    # -- Dashboard --------------------------------------------------------------

    def me(self) -> dict:
        return self._get("/me")

    def credits(self) -> dict:
        return self._get("/credits")

    def keys(self) -> list:
        res = self._get("/keys")
        return res.get("keys", [])

    def create_key(self, name: str = "Default") -> dict:
        return self._post("/keys", {"name": name})

    def revoke_key(self, key_id: str) -> None:
        self._delete(f"/keys/{key_id}")

    def usage(self, *, limit: int = 50, offset: int = 0) -> dict:
        return self._get("/usage", limit=limit, offset=offset)

    def checkout(self, pack_id: str) -> dict:
        return self._post("/checkout", {"pack_id": pack_id})
