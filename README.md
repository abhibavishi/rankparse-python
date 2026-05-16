# rankparse

Official Python SDK for the [RankParse](https://rankparse.com) SEO API.

RankParse gives you cheap, programmatic access to 25+ SEO signals — backlinks, domain authority, tech stack, page metadata, and more — powered by pre-processed Common Crawl data.

## Install

```bash
pip install rankparse
```

Requires Python 3.9+ and installs `httpx` automatically.

## Quick start

**Sync:**

```python
from rankparse import RankParseClient

client = RankParseClient(api_key="rp_...")

result = client.domain_authority("github.com")
print(result["data"])
# {"domain": "github.com", "score": 94, "backlinks": 12400000, ...}
```

**Async:**

```python
import asyncio
from rankparse import AsyncRankParseClient

async def main():
    client = AsyncRankParseClient(api_key="rp_...")
    result = await client.domain_authority("github.com")
    print(result["data"])

asyncio.run(main())
```

**Context managers** (recommended for connection cleanup):

```python
with RankParseClient(api_key="rp_...") as client:
    da = client.domain_authority("example.com")
    bl = client.backlinks("example.com", limit=50)
```

```python
async with AsyncRankParseClient(api_key="rp_...") as client:
    da = await client.domain_authority("example.com")
```

## Error handling

```python
from rankparse import RankParseClient
from rankparse.errors import (
    AuthError,
    InsufficientCreditsError,
    NotFoundError,
    RateLimitError,
    APIError,
    RankParseError,
)

client = RankParseClient(api_key="rp_...")

try:
    result = client.backlinks("example.com")
except AuthError:
    print("Invalid API key")
except InsufficientCreditsError:
    print("Out of credits — buy more at rankparse.com/dashboard")
except RateLimitError:
    print("Rate limited — slow down")
except NotFoundError:
    print("Resource not found")
except APIError as e:
    print(f"API error {e.status}: {e}")
except RankParseError as e:
    print(f"Unexpected error: {e}")
```

All exceptions expose `.status` (HTTP status code) and `.code` (API error code string).

## Response envelope

Every response is a dict with this shape:

```json
{
  "data": [...],
  "credits_used": 2,
  "credits_remaining": 998,
  "domain": "example.com",
  "total": 1234,
  "limit": 100,
  "offset": 0
}
```

Fields `domain`, `url`, `total`, `limit`, and `offset` are only present when relevant.

## All methods

### Link graph

| Method | Description | Key params | Credits |
|---|---|---|---|
| `backlinks(domain)` | Inbound links to this domain | `limit`, `offset`, `sort`, `from_domain`, `link_type` | 2 |
| `referring_domains(domain)` | Unique domains linking to this domain | `limit`, `offset` | 2 |
| `outbound_links(domain)` | Links pointing out from this domain | `limit` | 2 |
| `anchor_text(domain)` | Anchor text distribution for inbound links | `limit` | 2 |
| `link_velocity(domain)` | Rate of link acquisition over time | — | 0 (v1 stub) |
| `new_links(domain)` | Recently acquired links | — | 0 (v1 stub) |
| `lost_links(domain)` | Recently lost links | — | 0 (v1 stub) |
| `link_intersect(domain_a, domain_b)` | Domains linking to both targets | `limit` | 5 |

### Domain intelligence

| Method | Description | Key params | Credits |
|---|---|---|---|
| `domain_authority(domain)` | DA score, backlink count, RDAP info, Tranco rank | — | 1 |
| `domain_rank(domain)` | Popularity rank | — | 2 |
| `domain_overlap(domains)` | Shared linking domains across a list | `limit` | 5 |
| `similar_domains(domain)` | Domains with similar link profiles | `limit` | 5 |
| `competitor_gap(domain, vs)` | Links pointing to competitor but not you | `limit` | 5 |
| `link_audit(domain)` | Toxic/spammy link signals | — | 2 |
| `site_explorer(domain)` | Full domain overview | `limit` | 10 |

### Page / site

| Method | Description | Key params | Credits |
|---|---|---|---|
| `page_seo(url)` | On-page SEO signals | — | 2 |
| `page_performance(url)` | Google PageSpeed Insights + Core Web Vitals | `strategy` | 3 |
| `tech_stack(url)` | Technologies detected on the page | — | 2 |
| `site_health(domain)` | Crawl errors, redirect chains, status codes | — | 2 |
| `sitemap(domain)` | Sitemap URLs | — | 2 |
| `crawl_history(domain)` | Crawl timestamps and HTTP status history | `limit`, `offset` | 2 |
| `schema_markup(url)` | Structured data / JSON-LD | — | 0 (v1 stub) |
| `internal_links(url)` | Internal link graph for a page | `limit`, `offset` | 0 (v1 stub) |
| `top_pages(domain)` | Most-linked pages on a domain | `limit` | 2 |

### Batch

| Method | Description | Credits |
|---|---|---|
| `batch(requests)` | Run multiple endpoint calls in one request | Sum of individual costs |

```python
result = client.batch([
    {"endpoint": "domain-authority", "domain": "github.com"},
    {"endpoint": "backlinks", "domain": "github.com", "limit": 10},
])
```

### Dashboard (no credits)

| Method | Description |
|---|---|
| `me()` | Your profile and credit balance |
| `credits()` | Current credit balance |
| `keys()` | List your API keys (returns a plain list) |
| `create_key(name)` | Create a new API key (returns raw key once) |
| `revoke_key(key_id)` | Revoke an API key |
| `usage(limit, offset)` | Paginated usage logs |
| `checkout(pack_id)` | Create a Stripe checkout session for credit top-up |

## Configuration

```python
client = RankParseClient(
    api_key="rp_...",
    base_url="https://api.rankparse.com/v1",  # default
    timeout=30.0,  # seconds, default 30
)
```

## License

MIT
