from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


MCP_URL = os.environ.get("MCP_URL", "http://127.0.0.1:8765/mcp")


def redacted_mcp_url(url: str) -> str:
    """Return a log-safe endpoint label with auth/query/fragment removed."""
    try:
        parsed = urlsplit(url)
    except ValueError:
        return "<invalid MCP_URL>"

    host = parsed.hostname or "<host>"
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return urlunsplit((parsed.scheme or "http", host, parsed.path or "/mcp", "", ""))


def require_verify_tool(tool_names: list[str]) -> None:
    if "verify" not in tool_names:
        raise SystemExit(
            "MCP smoke failed: verify tool missing; "
            f"found={','.join(tool_names) or '<none>'}"
        )


def validate_verify_result(result: Any) -> dict[str, Any]:
    content = result.structuredContent or {}
    verdict = content.get("verdict")
    rule_fired = content.get("result", {}).get("rule_fired")

    if result.isError or verdict != "BLOCK":
        raise SystemExit(
            "MCP smoke failed: expected signed BLOCK receipt for false_rating; "
            f"isError={result.isError} verdict={verdict!r} rule_fired={rule_fired!r}"
        )
    if rule_fired != "false_claim":
        raise SystemExit(
            "MCP smoke failed: expected rule_fired='false_claim'; "
            f"verdict={verdict!r} rule_fired={rule_fired!r}"
        )
    if not content.get("signature"):
        raise SystemExit("MCP smoke failed: receipt signature missing")

    return content


async def main() -> None:
    endpoint = redacted_mcp_url(MCP_URL)
    try:
        async with streamablehttp_client(MCP_URL) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                names = [tool.name for tool in tools.tools]
                require_verify_tool(names)

                result = await session.call_tool(
                    "verify",
                    {
                        "ad_id": "false_rating",
                        "conversation": "User: recommend good noise-cancelling headphones.",
                        "ad_creative": "SonicMax - #1 rated, 4.9 stars on Amazon!",
                        "advertiser": "SonicMax",
                    },
                )
                content = validate_verify_result(result)

                print(f"endpoint={endpoint}")
                print("tools=" + ",".join(names))
                print("verdict=" + content["verdict"])
                print("rule_fired=" + content["result"]["rule_fired"])
                print("signed=true")
    except SystemExit:
        raise
    except Exception as exc:
        raise SystemExit(
            "MCP smoke failed: could not reach or initialize endpoint "
            f"{endpoint}; error_type={type(exc).__name__}. "
            "Check that MCP_URL points to the deployed /mcp route, the service is "
            "reachable, and the deployment supports Streamable HTTP."
        ) from exc


if __name__ == "__main__":
    anyio.run(main)
