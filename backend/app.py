# backend/app.py
from fastapi import FastAPI, WebSocket
import asyncio
from starlette.websockets import WebSocket, WebSocketDisconnect
import random

app = FastAPI()

stocks_data = [
    {"ticker": "A", "open": 137.24, "refreshInterval": 2},
    {"ticker": "AA", "open": 29.93, "refreshInterval": 4},
    {"ticker": "AAA", "open": 25, "refreshInterval": 3},
    {"ticker": "AADR", "open": 48.4499, "refreshInterval": 5},
    {"ticker": "AAGC", "open": 0.0007, "refreshInterval": 2},
    {"ticker": "AAAU", "open": 18.62, "refreshInterval": 3},
    {"ticker": "AABB", "open": 0.03325, "refreshInterval": 5},
    {"ticker": "AAGFF", "open": 0.25, "refreshInterval": 4},
    {"ticker": "AAGIY", "open": 44.15, "refreshInterval": 5},
    {"ticker": "AACAY", "open": 2.15, "refreshInterval": 3},
    {"ticker": "AACG", "open": 1.42, "refreshInterval": 2},
    {"ticker": "AACI", "open": 10.165, "refreshInterval": 2},
    {"ticker": "AAIGF", "open": 11.33, "refreshInterval": 3},
    {"ticker": "AACIW", "open": 0.035, "refreshInterval": 4},
    {"ticker": "AAIN", "open": 23.42, "refreshInterval": 3},
    {"ticker": "AAL", "open": 14.25, "refreshInterval": 5},
    {"ticker": "AAMC", "open": 7.2794, "refreshInterval": 2},
    {"ticker": "AAME", "open": 2.55, "refreshInterval": 5},
    {"ticker": "AACTF", "open": 0.041, "refreshInterval": 3},
    {"ticker": "AAMMF", "open": 0.26, "refreshInterval": 5},
]

connections = {idx: set() for idx in range(len(stocks_data))}

selected_stocks = set()

async def update_stock_prices():
    while True:
        for stock_idx in selected_stocks:
            stock = stocks_data[stock_idx]
            stock["open"] = round(stock["open"] * (1 + random.uniform(-0.02, 0.02)), 5)
            for connection in connections[stock_idx]:
                await connection.send_json({stock["ticker"]: stock["open"]})
        await asyncio.sleep(min(stock["refreshInterval"] for stock in stocks_data))

async def start_stock_updates():
    tasks = [update_stock_prices()]
    await asyncio.gather(*tasks)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_stock_updates())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = int(await websocket.receive_text())
        selected_stocks.update(range(data))
        for stock_idx in range(data):
            connections[stock_idx].add(websocket)
            stock = stocks_data[stock_idx]
            await websocket.send_json({stock["ticker"]: stock["open"]})

        while True:
            for stock_idx in selected_stocks:
                stock = stocks_data[stock_idx]
                stock["open"] = round(stock["open"] * (1 + random.uniform(-0.02, 0.02)), 8)
                await websocket.send_json({stock["ticker"]: stock["open"]})
                await asyncio.sleep(stock["refreshInterval"])

    except WebSocketDisconnect:
        pass
    finally:
        for idx in connections:
            connections[idx].discard(websocket)