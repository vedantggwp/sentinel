from __future__ import annotations

import json
from pathlib import Path

import httpx

from sentinel.config import settings
from sentinel.contracts import AdRequest

SCENARIOS_PATH = Path("data/scenarios.json")


async def get_ad_request(
    conversation: str,
    scenario_id: str | None = None,
) -> AdRequest:
    if settings.thrad_api_key and settings.thrad_api_url:
        live = await _fetch_live_ad(conversation)
        if live:
            return live

    return _mock_ad_request(conversation, scenario_id)


async def _fetch_live_ad(conversation: str) -> AdRequest | None:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                settings.thrad_api_url,
                headers={"Authorization": f"Bearer {settings.thrad_api_key}"},
                json={"conversation": conversation},
            )
            response.raise_for_status()
            return _normalize(response.json(), conversation)
    except Exception:
        return None


def _normalize(payload: dict, conversation: str) -> AdRequest:
    ad = payload.get("ad", payload)
    return AdRequest(
        ad_id=str(ad.get("id") or ad.get("ad_id") or "thrad-live"),
        conversation=conversation,
        ad_creative=str(ad.get("creative") or ad.get("ad_creative") or ad.get("copy")),
        advertiser=ad.get("advertiser") or ad.get("brand"),
        landing_url=ad.get("landing_url") or ad.get("url"),
    )


def _mock_ad_request(conversation: str, scenario_id: str | None = None) -> AdRequest:
    scenarios = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))
    scenario = next(
        (item for item in scenarios if item["id"] == scenario_id),
        scenarios[0],
    )
    return AdRequest(
        ad_id=scenario["id"],
        conversation=conversation or scenario["conversation"],
        ad_creative=scenario["ad_creative"],
        advertiser=scenario.get("advertiser"),
    )
