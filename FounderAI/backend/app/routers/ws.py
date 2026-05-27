"""
WebSocket endpoint: /ws/{blueprint_id}

Subscribes to Redis pub/sub channel for the blueprint and streams
live agent updates to the connected browser.
"""
from __future__ import annotations

import asyncio
import json

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..config import settings

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{blueprint_id}")
async def websocket_endpoint(websocket: WebSocket, blueprint_id: str):
    await websocket.accept()
    channel = f"blueprint:{blueprint_id}"

    r = aioredis.from_url(settings.redis_url, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe(channel)

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    await websocket.send_text(message["data"])
                except WebSocketDisconnect:
                    break
                # Stop streaming once the pipeline is done
                data = json.loads(message["data"])
                if data.get("type") in ("completed", "error"):
                    break
    except (WebSocketDisconnect, asyncio.CancelledError):
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await r.aclose()
        try:
            await websocket.close()
        except Exception:
            pass
