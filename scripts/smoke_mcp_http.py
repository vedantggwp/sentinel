from __future__ import annotations

import os

import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


MCP_URL = os.environ.get("MCP_URL", "http://127.0.0.1:8765/mcp")


async def main() -> None:
    async with streamablehttp_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]
            if "verify" not in names:
                raise SystemExit(f"verify tool missing; found {names}")

            result = await session.call_tool(
                "verify",
                {
                    "ad_id": "false_rating",
                    "conversation": "User: recommend good noise-cancelling headphones.",
                    "ad_creative": "SonicMax - #1 rated, 4.9 stars on Amazon!",
                    "advertiser": "SonicMax",
                },
            )
            content = result.structuredContent or {}
            if result.isError or content.get("verdict") != "BLOCK":
                raise SystemExit(f"unexpected MCP result: {result}")
            if content.get("result", {}).get("rule_fired") != "false_claim":
                raise SystemExit(f"unexpected rule: {content}")
            if not content.get("signature"):
                raise SystemExit("MCP receipt was not signed")

            print("tools=" + ",".join(names))
            print("verdict=" + content["verdict"])
            print("rule_fired=" + content["result"]["rule_fired"])
            print("signed=true")


if __name__ == "__main__":
    anyio.run(main)
