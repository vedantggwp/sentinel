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


def _normalize(payload: dict, conversation: str) -> AdRequest | None:
    if not isinstance(payload, dict):
        return None

    ad = _candidate_ad(payload)
    if not isinstance(ad, dict):
        return None

    creative = _first_text(
        ad,
        "creative",
        "ad_creative",
        "copy",
        "body",
        "text",
        "description",
        "adm",
    )
    if not creative:
        return None

    return AdRequest(
        ad_id=_first_text(ad, "id", "ad_id", "bid_id", "creative_id") or "thrad-live",
        conversation=conversation,
        ad_creative=creative,
        advertiser=_first_text(ad, "advertiser", "brand", "advertiser_name", "adomain"),
        landing_url=_first_text(ad, "landing_url", "url", "click_url", "nurl"),
    )


def _candidate_ad(payload: dict) -> dict | None:
    if isinstance(payload.get("ad"), dict):
        return payload["ad"]
    if isinstance(payload.get("bid"), dict):
        return payload["bid"]
    if isinstance(payload.get("ads"), list) and payload["ads"]:
        return payload["ads"][0] if isinstance(payload["ads"][0], dict) else None

    seatbids = payload.get("seatbid")
    if isinstance(seatbids, list) and seatbids:
        bids = seatbids[0].get("bid") if isinstance(seatbids[0], dict) else None
        if isinstance(bids, list) and bids:
            return bids[0] if isinstance(bids[0], dict) else None

    return payload


def _first_text(ad: dict, *keys: str) -> str | None:
    for key in keys:
        value = ad.get(key)
        if value is None and isinstance(ad.get("ext"), dict):
            value = ad["ext"].get(key)
        text = _string_value(value)
        if text:
            return text
    return None


def _string_value(value: object) -> str | None:
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        for item in value:
            text = _string_value(item)
            if text:
                return text
    return None


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
