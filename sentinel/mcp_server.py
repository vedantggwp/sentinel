from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from sentinel.attest import create_attestation
from sentinel.config import settings
from sentinel.contracts import AdRequest, Attestation
from sentinel.pipeline import run_pipeline


mcp = FastMCP("Sentinel", host="0.0.0.0", port=settings.port)


@mcp.tool()
def verify(
    ad_id: str,
    conversation: str,
    ad_creative: str,
    advertiser: str | None = None,
    landing_url: str | None = None,
) -> Attestation:
    ad = AdRequest(
        ad_id=ad_id,
        conversation=conversation,
        ad_creative=ad_creative,
        advertiser=advertiser,
        landing_url=landing_url,
    )
    result = run_pipeline(ad)
    return create_attestation(ad, result)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
